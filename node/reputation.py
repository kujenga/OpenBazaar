import json
from protocol import proto_reputation, proto_query_reputation
from collections import defaultdict
from pyelliptic import ECC
import logging

def review(pubkey, subject, signature, text, rating):
    data = {}
    # this is who signs
    data['pubkey'] = pubkey.encode('hex')
    # this is who the review is about
    data['subject'] = subject.encode('hex')
    # the signature
    data['sig'] = signature.encode('hex')
    # some text
    data['text'] = text
    # rating
    data['rating'] = rating
    return data

class Reputation(object):
    def __init__(self, transport):

        self._transport = transport
        self._priv = transport._myself

        # TODO: Pull reviews out of persistent storage
        self._reviews = defaultdict(list)

        transport.add_callback('reputation', self.on_reputation)
        transport.add_callback('query_reputation', self.on_query_reputation)

        # SAMPLE Review because there is no persistence of reviews ATM
        #self.create_review(self._priv.get_pubkey(), "Initial Review", 10)

        self._log = logging.getLogger(self.__class__.__name__)


    # getting reputation from inside the application
    def get_reputation(self, pubkey):
        return self._reviews[pubkey]


    def get_my_reputation(self):
        return self._reviews[self._priv.get_pubkey()]


    # Create a new review and broadcast to the network
    def create_review(self, pubkey, text, rating):

        signature = self._priv.sign(self._build_review(pubkey, text, rating))

        new_review = review(self._priv.get_pubkey(), pubkey, signature, text, rating)
        self._reviews[pubkey].append(new_review)

        # Broadcast the review
        self._transport.send(proto_reputation(pubkey, [new_review]))


    # Build JSON for review to be signed
    def _build_review(self, pubkey, text, rating):
        return json.dumps([pubkey.encode('hex'),  text, rating])


	# Query reputation for pubkey from the network
    def query_reputation(self, pubkey):
        self._transport.send(proto_query_reputation(pubkey))


	#
    def parse_review(self, msg):

        pubkey = msg['pubkey'].decode('hex')
        subject = msg['subject'].decode('hex')
        signature = msg['sig'].decode('hex')
        text = msg['text']
        rating = msg['rating']

        # check the signature
        valid = ECC(pubkey=pubkey).verify(signature, self._build_review(subject, str(text), rating))

        if valid:
            newreview = review(pubkey, subject, signature, text, rating)

            if newreview not in self._reviews[subject]:
                self._reviews[subject].append(newreview)

        else:
            self._log.info("[reputation] Invalid review!")


    # callbacks for messages
    # a new review has arrived
    def on_reputation(self, msg):
        for review in msg.get('reviews', []):
            self.parse_review(review)

    # query reviews has arrived
    def on_query_reputation(self, msg):
        pubkey = msg['pubkey'].decode('hex')
        if pubkey in self._reviews:
            self._transport.send(proto_reputation(pubkey, self._reviews[pubkey]))


if __name__ == '__main__':
    class FakeTransport():
        _myself = ECC(curve='secp256k1')
        def add_callback(self, section, cb):
            pass
        def send(self, msg):
            print 'sending', msg
        def log(self, msg):
            print msg
    transport = FakeTransport()
    rep = Reputation(transport)
    print rep.get_reputation(transport._myself.get_pubkey())
    print rep.get_my_reputation()
