from protocol import shout, proto_page, query_page
from reputation import Reputation
from orders import Orders
import protocol
import sys
import json
import lookup
from pymongo import MongoClient
import logging
import pyelliptic
import pycountry
from ecdsa import SigningKey,SECP256k1
import random
from obelisk import bitcoin
import base64
import pickle

# for entangled implementation
from twisted.internet import defer, reactor
import hashlib
import entangled.node
from entangled.kademlia.datastore import SQLiteDataStore
import entangled.kademlia.constants

class Market(object):

    def __init__(self, transport, node, store_file):

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

        # store file
        self.store_file = store_file
        # assign Entangled Node to global
	self.node = node

        # Connect to database
        MONGODB_URI = 'mongodb://localhost:27017'
        _dbclient = MongoClient()
        self._db = _dbclient.openbazaar
        print type(self._db)
        self.settings = self._db.settings.find_one()

        welcome = True

        if self.settings:
            if  'welcome' in self.settings.keys() and self.settings['welcome']:
                welcome = False
        else:
            # creates the settings collection if it does not already exist
            # self.settings = self._db.create_collection('settings')
            pass


        # Register callbacks for incoming events
        transport.add_callback('query_myorders', self.on_query_myorders)
        transport.add_callback('peer', self.on_peer)
        transport.add_callback('query_page', self.on_query_page)
        transport.add_callback('page', self.on_page)
        transport.add_callback('negotiate_pubkey', self.on_negotiate_pubkey)
        transport.add_callback('proto_response_pubkey', self.on_response_pubkey)

        # loads the page in from memory
        self.load_page(welcome)
        # stored the page in the DHT once the reactor has been given time to startup and the entangled node has refreshed
        delay = 1.0
        reactor.callLater(delay, self.store_page)


    def generate_new_secret(self):

        key = bitcoin.EllipticCurveKey()
        key.new_key_pair()
        hexkey = key.secret.encode('hex')

        self._log.info('Pubkey generate: %s' % key._public_key.pubkey)

        self._db.settings.update({}, {"$set": {"secret":hexkey, "pubkey":bitcoin.GetPubKey(key._public_key.pubkey, False).encode('hex')}})


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
        if nickname in self._transport.nick_mapping:
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
    def load_page(self, welcome):

        self._log.info("Loading market config from %s." % self.store_file)

        with open(self.store_file) as f:
            data = json.loads(f.read())

        self._log.info("Configuration data: " + json.dumps(data))

        assert "desc" in data
        nickname = data["nickname"]
        desc = data["desc"]
                
        # unused mongodb ish from upstream merge
        #nickname = self.settings['nickname'] if self.settings.has_key("nickname") else ""
        #storeDescription = self.settings['storeDescription'] if self.settings.has_key("storeDescription") else ""
       
        tagline = "%s: %s" % (nickname, desc) #, storeDescription)
        self.mypage = tagline
        self.nickname = nickname
        self.signature = self._transport._myself.sign(tagline)

        if welcome:
            self._db.settings.update({}, {"$set":{"welcome":"noshow"}})
        else:
            self.welcome = False

        self._log.info("Tagline signature: " + self.signature.encode("hex"))
        

    # loads your file into the DHT *********************************************************
    def store_page(self):

        # callback functons for DHT input
        def publish_succ(result):
            print("DHT iterativeStore operation completed with result: ~"+str(result)+"~")
            if (result != None):
                self._log.info("DHT publish result: " + str(result))
        def publish_err(error):
            print("error while publishing page into DHT: %s"%error)
            self._log.info("DHT publish error: %s" % error)

        # publish local site into the DHT (pickle.dumps() makes str from dict)
        page_data = pickle.dumps(proto_page(self._transport._myself.get_pubkey(),
                                            self.mypage, self.signature,
                                            self.nickname))

        #print "pickle.dumps(page_data): %s" % page_data
        #print "pickle.loads(page_data): %s" % (pickle.loads(page_data))

        # creates a sha1 has of the current public key to get it into hashtable format
        h = hashlib.sha1()
        h.update(self._transport._myself.get_pubkey())
        key = h.digest()
        
        print "attempting iterativeStore with contacts:"
        self.node.printContacts()
        deferred = self.node.iterativeStore(key, page_data, originalPublisherID = self.node._generateID())
        deferred.addCallbacks(publish_succ, errback = publish_err)
        

    # PAGE QUERYING

    def query_page(self, pubkey):
        # this is the old way that the pages were retreived over p2p
        #self._transport.send(query_page(pubkey))

        print("querying for page through entangled with contacts:")
        self.node.printContacts()
        # creates a sha1 has of the current public key to get it into the format used by the publishData method in load_pagex
        h = hashlib.sha1()
        h.update(pubkey)
        key = h.digest()

        # callbacks for entangled node interactions
        def retrieved_page(result):
            # parses in retreived page and stores it locally in self.pages
            if (len(result) > 0):

                self._log.info("for key: " + key + " iteratve find returned result: " + str(result))
				# pickle.loads() goes from str to dict
                page = pickle.loads(result[key])
                #print "result[key]: %s" % result[key]
                pubkey_in = page.get('pubkey')
                page_in = page.get('text')
                print "retreived page: %s" % page
                if pubkey_in and page_in:
                    self.pages[pubkey_in] = page_in
            else:
                print("search for key %s failed to retrieve any pages" % key)
                self._log.info("for key: "+key+" iteratve find returned nothing")
            
        # searches for the value associated with sha1 has of the pubkey for the specified nodex
        df = self.node.iterativeFindValue(key)
        df.addCallback(retrieved_page)
        

    def on_page(self, page):

        raise Exception("You should be using Entangled!")

        self._log.info("Page returned: " + str(page))

        pubkey = page.get('pubkey')
        page = page.get('text')

        if pubkey and page:
            self._log.info(page)
            self.pages[pubkey] = page

    # Return your page info if someone requests it on the network

    # this will be unnecessary when the DHT is implemented ----------------------------------------------------
    def on_query_page(self, peer):
        
        raise Exception("You should be using Entangled!")
        
        self._log.info("Someone is querying for your page")
        self._transport.send(proto_page(self._transport._myself.get_pubkey(),
                                        self.mypage, self.signature,
                                        self.nickname))
        '''
        self.settings = self.get_settings()
        self._log.info(base64.b64encode(self.settings['storeDescription'].encode('ascii')))
        self._transport.send(proto_page(self._transport._myself.get_pubkey().encode('hex'),
                                        self.settings['storeDescription'], self.signature,
                                        self.settings['nickname']))
        '''

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


    # Products
    def save_product(self, msg):
        self._log.info("Product to save %s" % msg)
        self._log.info(self._transport)

        product_id = msg['id'] if msg.has_key("id") else ""

        if product_id == "":
          product_id = random.randint(0,1000000)

        if not msg.has_key("productPrice") or not msg['productPrice'] > 0:
          msg['productPrice'] = 0

        if not msg.has_key("productQuantity") or not msg['productQuantity'] > 0:
          msg['productQuantity'] = 1

        self._db.products.update({'id':product_id}, {'$set':msg}, True)
        

    def remove_product(self, msg):
        self._log.info("Product to remove %s" % msg)
        self._db.products.remove({'id':msg['productID']})


    def get_products(self):
        self._log.info(self._transport.market_id)
        products = self._db.products.find()
        my_products = []

        for product in products:
          my_products.append({ "productTitle":product['productTitle'] if product.has_key("productTitle") else "",
                        "id":product['id'] if product.has_key("id") else "",
                        "productDescription":product['productDescription'] if product.has_key("productDescription") else "",
                        "productPrice":product['productPrice'] if product.has_key("productPrice") else "",
                        "productShippingPrice":product['productShippingPrice'] if product.has_key("productShippingPrice") else "",
                        "productTags":product['productTags'] if product.has_key("productTags") else "",
                        "productImageData":product['productImageData'] if product.has_key("productImageData") else "",
                        "productQuantity":product['productQuantity'] if product.has_key("productQuantity") else "",
                         })

        return { "products": my_products }


    # SETTINGS - should be stored locally

    def save_settings(self, msg):
        self._log.info("Settings to save %s" % msg)
        self._log.info(self._transport)
        self._db.settings.update({'id':'%s'%self._transport.market_id}, {'$set':msg}, True)

    def get_settings(self):
        self._log.info(self._transport.market_id)
        settings = self._db.settings.find_one({'id':'%s'%self._transport.market_id})
        print "settings: %s" % settings
        if settings:
            return { "bitmessage": settings['bitmessage'] if settings.has_key("bitmessage") else "",
                "email": settings['email'] if settings.has_key("email") else "",
                "PGPPubKey": settings['PGPPubKey'] if settings.has_key("PGPPubKey") else "",
                "pubkey": settings['pubkey'] if settings.has_key("pubkey") else "",
                "nickname": settings['nickname'] if settings.has_key("nickname") else "",
                "secret": settings['secret'] if settings.has_key("secret") else "",
                "welcome": settings['welcome'] if settings.has_key("welcome") else "",
                "escrowAddresses": settings['escrowAddresses'] if settings.has_key("escrowAddresses") else "",
                "storeDescription": settings['storeDescription'] if settings.has_key("storeDescription") else "",
                "city": settings['city'] if settings.has_key("city") else "",
                "stateRegion": settings['stateRegion'] if settings.has_key("stateRegion") else "",
                "street1": settings['street1'] if settings.has_key("street1") else "",
                "street2": settings['street2'] if settings.has_key("street2") else "",
                "countryCode": settings['countryCode'] if settings.has_key("countryCode") else "",
                "zip": settings['zip'] if settings.has_key("zip") else "",
                "arbiterDescription": settings['arbiterDescription'] if settings.has_key("arbiterDescription") else "",
                "arbiter": settings['arbiter'] if settings.has_key("arbiter") else "",
                }
