from protocol import shout, proto_page, query_page
from reputation import Reputation
from orders import Orders
import protocol
import sys
import json
import lookup
from pymongo import MongoClient
import logging

# for entangled implementation
from twisted.internet import defer
from twisted.internet.protocol import Protocol, ServerFactory, ClientCreator

import hashlib

import entangled.node
from entangled.kademlia.datastore import SQLiteDataStore


class Market(object):

    def __init__(self, transport, node):

        self._log = logging.getLogger(self.__class__.__name__)
        self._log.info("Initializing")

        # for now we have the id in the transport
        self._myself = transport._myself
        self._peers = transport._peers
        self._transport = transport
        self.query_ident = None

        self.reputation = Reputation(self._transport)
        self.orders = Orders(self._transport)
        self.order_entries = self.orders._orders

        # TODO: Persistent storage of nicknames and pages
        self.nicks = {}
        self.pages = {}

        # Connect to database
        MONGODB_URI = 'mongodb://localhost:27017'         
        _dbclient = MongoClient()
        self._db = _dbclient.openbazaar

        # Register callbacks for incoming events
        transport.add_callback('query_myorders', self.on_query_myorders)
        transport.add_callback('peer', self.on_peer)
        transport.add_callback('query_page', self.on_query_page)
        transport.add_callback('page', self.on_page)
        transport.add_callback('negotiate_pubkey', self.on_negotiate_pubkey)
        transport.add_callback('proto_response_pubkey', self.on_response_pubkey)

        # store Entangled node for replication in the network
        self.node = node

        self.load_page()

        # Send Market Shout
        transport.send(shout({'text': 'Market Initialized'}))


##########################################################################
# continue implementing the use of the Entangled node from this point
##########################################################################

    # returns a public key for a given nickname
    def lookup(self, msg):

        if self.query_ident is None:
            self._log.info("Initializing identity query")
            self.query_ident = lookup.QueryIdent()

        nickname = str(msg["text"])
        key = self.query_ident.lookup(nickname)
        if key is None:
            self._log.info("Key not found for this nickname")
            return ("Key not found for this nickname", None)

        self._log.info("Found key: %s " % key.encode("hex"))
        if nickname in self._transport.nick_mapping.has_key:
            self._log.info("Already have a cached mapping, just adding key there.")
            response = {'nickname': nickname,
                        'pubkey': self._transport.nick_mapping[nickname][1].encode('hex'),
                        'signature': self._transport.nick_mapping[nickname][0].encode('hex'),
                        'type': 'response_pubkey',
                        'signature': 'unknown'}
            self._transport.nick_mapping[nickname][0] = key
            return (None, response)

        self._transport.nick_mapping[nickname] = [key, None]
        self._transport.send(protocol.negotiate_pubkey(nickname, key))

    # Load default information for your market from your file
    # loads your file into the DHT *************************************************************************
    def load_page(self):

        self._log.info("Loading market config from " + sys.argv[1])

        with open(sys.argv[1]) as f:
            data = json.loads(f.read())

        self._log.info("Configuration data: " + json.dumps(data))    

        assert "desc" in data
        nickname = data["nickname"]
        desc = data["desc"]

        # unnecessary as instance variables with the DHT usage
        tagline = "%s: %s" % (nickname, desc)
        self.mypage = tagline
        self.nickname = nickname
        self.signature = self._transport._myself.sign(tagline)

        # callback functons for DHT input
        def publish_succ(result = None):
            self._log.info("DHT publish result: " + result)
        def publish_err(error = None):
            self._log.info("DHT publish error: " + error)
        # publish local site into the DHT
        page_data = proto_page(self._transport._myself.get_pubkey(),
                                        self.mypage, self.signature,
                                        self.nickname)
        # this publish operation uses the public key of this user as the key for the DHT network
        # unfortunately, the publishData method hashes this value, so it is not directly used as the key
        # retreive operation needs to reflect this
        deferred = self.node.publishData(self._transport._myself.get_pubkey(),page_data)
        deferred.addCallbacks(publish_succ, errback = publish_err)

        self._log.info("Tagline signature: " + self.signature.encode("hex"))


    # SETTINGS - should be stored locally

    def save_settings(self, msg):
        self._db.settings.update({}, msg, True)

    def get_settings(self):

        settings = self._db.settings.find_one()

        if settings:
            return {"bitmessage": settings['bitmessage'] if settings.has_key("bitmessage") else "",
                    "email": settings['email'] if settings.has_key("email") else "",
                    "PGPPubKey": settings['PGPPubKey'] if settings.has_key("PGPPubKey") else "",
                    "pubkey": settings['pubkey'] if settings.has_key("pubkey") else "",
                    "nickname": settings['nickname'] if settings.has_key("nickname") else "",
                    "secret": settings['secret'] if settings.has_key("secret") else "",
                    }


    # PAGE QUERYING

    # Alter these significantly to use the DHT +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def query_page(self, pubkey):
        # remove the next line when possible
        self._transport.send(query_page(pubkey))
        # creates a sha1 has of the current public key to get it into the format used by the publishData method in load_pagex
        h = hashlib.sha1()
        h.update(pubkey)
        key = h.digest()

        # callbacks for entangled node interactions
        def retrieved_page(result):
            # parses in retreived page and stores it locally in self.pages
            page = result[key]
            self._log.info("for key: "+key+" iteratve find returned: "+result[key])
            pubkey_in = page.get('pubkey')
            page_in = page.get('text')
            
            if pubkey_in and page_in:
                self.pages[pubkey_in] = page_in
        # searches for the value associated with sha1 has of the pubkey for the specified nodex
        df = self.node.iterativeFindValue(key)
        df.addCallback(retrieved_page)
        

    def on_page(self, page):
        self._log.info("Page returned: " + str(page))

        pubkey = page.get('pubkey')
        page = page.get('text')

        if pubkey and page:
            self.pages[pubkey] = page

    # Return your page info if someone requests it on the network

    # this will be unnecessary when the DHT is implemented ----------------------------------------------------
    def on_query_page(self, peer):
        self._log.info("Someone is querying for your page")
        self._transport.send(proto_page(self._transport._myself.get_pubkey(),
                                        self.mypage, self.signature,
                                        self.nickname))

    def on_query_myorders(self, peer):
        self._log.info("Someone is querying for your page")
        self._transport.send(proto_page(self._transport._myself.get_pubkey(),
                                        self.mypage, self.signature,
                                        self.nickname))

    def on_peer(self, peer):
        pass

    # may need to specifiy online vs. offline nodes for each site on the DHT.

    def on_negotiate_pubkey(self, ident_pubkey):
        self._log.info("Someone is asking for your real pubKey")
        assert "nickname" in ident_pubkey
        assert "ident_pubkey" in ident_pubkey
        nickname = ident_pubkey['nickname']
        ident_pubkey = ident_pubkey['ident_pubkey'].decode("hex")
        self._transport.respond_pubkey_if_mine(nickname, ident_pubkey)

    def on_response_pubkey(self, response):
        self._log.info("got a pubkey!")
        assert "pubkey" in response
        assert "nickname" in response
        assert "signature" in response
        pubkey = response["pubkey"].decode("hex")
        signature = response["signature"].decode("hex")
        nickname = response["nickname"]
        # Cache mapping for later.
        if nickname not in self._transport.nick_mapping:
            self._transport.nick_mapping[nickname] = [None, pubkey]
        # Verify signature here...
        # Add to our dict.
        self._transport.nick_mapping[nickname][1] = pubkey
        self._log.info("[market] mappings: ###############")
        for k, v in self._transport.nick_mapping.iteritems():
            self._log.info("'%s' -> '%s' (%s)" % (
                k, v[1].encode("hex") if v[1] is not None else v[1],
                v[0].encode("hex") if v[0] is not None else v[0]))
        self._log.info("##################################")
