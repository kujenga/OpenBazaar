import json
import pyelliptic as ec

from p2p import PeerConnection, TransportLayer
import traceback
from pymongo import MongoClient
from protocol import hello_request, hello_response, proto_response_pubkey
import obelisk
import logging
from market import Market
#from ecdsa import SigningKey,SECP256k1
#import random
from obelisk import bitcoin

class CryptoPeerConnection(PeerConnection):

    def __init__(self, transport, address, pub):
        self._priv = transport._myself
        self._pub = pub
        PeerConnection.__init__(self, transport, address)

    def encrypt(self, data):
        return self._priv.encrypt(data, self._pub)

    def send(self, data):
        self._log.info('DATA: %s', data)
        self.send_raw(self.encrypt(json.dumps(data)))

    def on_message(self, msg):
        # this are just acks
        pass


class CryptoTransportLayer(TransportLayer):

    def __init__(self, my_ip, my_port, market_id):

        TransportLayer.__init__(self, my_ip, my_port)

        self._myself = ec.ECC(curve='secp256k1')

        self.nick_mapping = {}

<<<<<<< HEAD
		# load nickname, secret and pubkey from store_file, which is a JSON file in ppl
        self.nickname, self.secret, self.pubkey = \
            self.load_crypto_details(store_file)
=======
        # Connect to database
        MONGODB_URI = 'mongodb://localhost:27017'
        _dbclient = MongoClient()
        self._db = _dbclient.openbazaar

        self.settings = self._db.settings.find_one({'id':"%s"%market_id})
        self.market_id = market_id

        if self.settings:
            self.nickname = self.settings['nickname'] if self.settings.has_key("nickname") else ""
            self.secret = self.settings['secret']
            self.pubkey = self.settings['pubkey']
        else:
            self.nickname = 'Default'
            key = bitcoin.EllipticCurveKey()
            key.new_key_pair()
            hexkey = key.secret.encode('hex')
            self._db.settings.insert({"id":'%s'%market_id, "secret":hexkey, "pubkey":bitcoin.GetPubKey(key._public_key.pubkey, False).encode('hex')})
            self.settings = self._db.settings.find_one({'id':"%s"%market_id})



#        self.nickname, self.secret, self.pubkey = \
#            self.load_crypto_details(store_file)

>>>>>>> upstream/master
        self._log = logging.getLogger(self.__class__.__name__)

    # Return data array with details from the crypto file
    # TODO: This needs to be protected better; potentially encrypted file or DB
    def load_crypto_details(self, store_file):
        with open(store_file) as f:
            data = json.loads(f.read())
        assert "nickname" in data
        assert "secret" in data
        assert "pubkey" in data
        assert len(data["secret"]) == 2 * 32
        assert len(data["pubkey"]) == 2 * 33

        return data["nickname"], data["secret"].decode("hex"), \
            data["pubkey"].decode("hex")

    def get_profile(self):
        peers = {}

        self.settings = self._db.settings.find_one({'id':"%s"%self.market_id})
        self._log.info('SETTINGS %s' % self.settings)
        for uri, peer in self._peers.iteritems():
            if peer._pub:
                peers[uri] = peer._pub.encode('hex')
        return {'uri': self._uri, 'pub': self._myself.get_pubkey().encode('hex'),'nickname': self.nickname,
                'peers': peers}

    def respond_pubkey_if_mine(self, nickname, ident_pubkey):

        if ident_pubkey != self.pubkey:
            self._log.info("Public key does not match your identity")
            return

        # Return signed pubkey
        pubkey = self._myself.pubkey
        ec_key = obelisk.EllipticCurveKey()
        ec_key.set_secret(self.secret)
        digest = obelisk.Hash(pubkey)
        signature = ec_key.sign(digest)

        # Send array of nickname, pubkey, signature to transport layer
        self.send(proto_response_pubkey(nickname, pubkey, signature))

    def pubkey_exists(self, pub):

        for uri, peer in self._peers.iteritems():
            self._log.info('PEER: %s Pub: %s' %
                           (peer._pub.encode('hex'), pub.encode('hex')))
            if peer._pub.encode('hex') == pub.encode('hex'):
                return True

        return False

    def create_peer(self, uri, pub):

        if pub:
            pub = pub.decode('hex')

        # Create the peer if public key is not already in the peer list
        # if not self.pubkey_exists(pub):
        self._peers[uri] = CryptoPeerConnection(self, uri, pub)

        # Call 'peer' callbacks on listeners
        self.trigger_callbacks('peer', self._peers[uri])

        # else:
        #    print 'Pub Key is already in peer list'

    def send_enc(self, uri, msg):
        peer = self._peers[uri]
        pub = peer._pub


        # Now send a hello message to the peer
        if pub:
            self._log.info("Sending encrypted [%s] message to %s"
                           % (msg['type'], uri))
            peer.send(msg)
        else:
            # Will send clear profile on initial if no pub
            self._log.info("Sending unencrypted [%s] message to %s"
                           % (msg['type'], uri))
            self._peers[uri].send_raw(json.dumps(msg))

    def init_peer(self, msg):
        self._log.info('Initialize Peer: %s' % msg)

        uri = msg['uri']
        pub = msg.get('pub')
        nickname = msg.get('nickname')
        msg_type = msg.get('type')

        if not self.valid_peer_uri(uri):
            self._log.info("Peer " + uri + " is not valid.")
            return

        if uri not in self._peers:
            # unknown peer
            self._log.info('Create New Peer: %s' % uri)
            self.create_peer(uri, pub)

            if not msg_type:
                self.send_enc(uri, hello_request(self.get_profile()))
            elif msg_type == 'hello_request':
                self.send_enc(uri, hello_response(self.get_profile()))

        else:
            # known peer
            if pub:
                # test if we have to update the pubkey
                if not self._peers[uri]._pub:
                    self._log.info("Setting public key for seed node")
                    self._peers[uri]._pub = pub.decode('hex')
                    self.trigger_callbacks('peer', self._peers[uri])

                if (self._peers[uri]._pub != pub.decode('hex')):
                    self._log.info("Updating public key for node")
                    self._peers[uri]._nickname = nickname
                    self._peers[uri]._pub = pub.decode('hex')

                    self.trigger_callbacks('peer', self._peers[uri])

            if msg_type == 'hello_request':
                # reply only if necessary
                self.send_enc(uri, hello_response(self.get_profile()))

    def on_raw_message(self, serialized):

        try:
            msg = json.loads(serialized)
            self._log.info("receive [%s]" % msg.get('type', 'unknown'))
        except ValueError:
            try:
                msg = json.loads(self._myself.decrypt(serialized))
                self._log.info("Decrypted raw message [%s]"
                               % msg.get('type', 'unknown'))
            except:
                self._log.info("incorrect msg ! %s..."
                               % self._myself.decrypt(serialized))
                traceback.print_exc()
                return

        msg_type = msg.get('type')
        msg_uri = msg.get('uri')

        if msg_type != '':

            if msg_type.startswith('hello') and msg_uri:
                self.init_peer(msg)
                for uri, pub in msg.get('peers', {}).iteritems():
                    # Do not add yourself as a peer
                    if uri != self._uri:
                        self.init_peer({'uri': uri, 'pub': pub})
                self._log.info("Update peer table [%s peers]" % len(self._peers))

            elif msg_type == 'goodbye' and msg_uri:
                self._log.info("Received goodbye from %s" % msg_uri)
                self.remove_peer(msg_uri)

            else:
                self.on_message(msg)
