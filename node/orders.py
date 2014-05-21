import json
from protocol import proto_reputation, proto_query_reputation, order
from collections import defaultdict
from pyelliptic import ECC
import random
from pymongo import MongoClient
from multisig import Multisig
import logging
import time


class Orders(object):
    def __init__(self, transport):
        self._transport = transport
        self._priv = transport._myself

        # TODO: Make user configurable escrow addresses
        self._escrows = ["02ca0020a9de236b47ca19e147cf2cd5b98b6600f168481da8ec0ca9ec92b59b76db1c3d0020f9038a585b93160632f1edec8278ddaeacc38a381c105860d702d7e81ffaa14d",
                         "02ca0020c0d9cd9bdd70c8565374ed8986ac58d24f076e9bcc401fc836352da4fc21f8490020b59dec0aff5e93184d022423893568df13ec1b8352e5f1141dbc669456af510c"]

        MONGODB_URI = 'mongodb://localhost:27017'
        _dbclient = MongoClient()
        self._db = _dbclient.openbazaar
        self._orders = self.get_orders()
        self.orders = self._db.orders

        transport.add_callback('order', self.on_order)
        self._log = logging.getLogger(self.__class__.__name__)

    def get_order(self, orderId):

        _order = self._db.orders.find_one({"id":orderId})

        # Get order prototype object before storing
        order = {"id":_order['id'],
                                    "state": _order['state'],
                                    "address": _order['address'] if _order.has_key("address") else "",
                                    "buyer": _order['buyer'] if _order.has_key("buyer") else "",
                                    "seller": _order['seller'] if _order.has_key("seller") else "",
                                    "escrows": _order['escrows'] if _order.has_key("escrows") else "",
                                    "text": _order['text'] if _order.has_key("text") else "",
                                    "created": _order['created'] if _order.has_key("created") else ""}
            #orders.append(_order)


        return order

    def get_orders(self):
        orders = []
        for _order in self._db.orders.find().sort([("created",-1)]):

            # Get order prototype object before storing
            orders.append({"id":_order['id'],
                                    "state": _order['state'],
                                    "address": _order['address'] if _order.has_key("address") else "",
                                    "buyer": _order['buyer'] if _order.has_key("buyer") else "",
                                    "seller": _order['seller'] if _order.has_key("seller") else "",
                                    "escrows": _order['escrows'] if _order.has_key("escrows") else "",
                                    "text": _order['text'] if _order.has_key("text") else "",
                                    "created": _order['created'] if _order.has_key("created") else ""})
            #orders.append(_order)


        return orders



    # Create a new order
    def create_order(self, seller, text):
        self._log.info('CREATING ORDER')
        id = random.randint(0,1000000)
        buyer = self._transport._myself.get_pubkey()
        new_order = order(id, buyer, seller, 'new', text, self._escrows)

        # Add a timestamp
        new_order['created'] = time.time()

        self._transport.send(new_order, seller)

        self._db.orders.insert(new_order)


    def accept_order(self, new_order):

    	# TODO: Need to have a check for the vendor to agree to the order

        new_order['state'] = 'accepted'
        seller = new_order['seller'].decode('hex')
        buyer = new_order['buyer'].decode('hex')

        new_order['escrows'] = [new_order.get('escrows')[0]]
        escrow = new_order['escrows'][0].decode('hex')

        # Create 2 of 3 multisig address
        self._multisig = Multisig(None, 2, [buyer, seller, escrow])

        new_order['address'] = self._multisig.address

        self._db.orders.update({ "id":new_order['id']}, {"$set":new_order}, True)

        self._transport.send(new_order, new_order['buyer'].decode('hex'))

    def pay_order(self, new_order): # action
        new_order['state'] = 'paid'
        self._db.orders.update({"id":new_order['id']}, {"$set":new_order}, True)
        new_order['type'] = 'order'
        self._transport.send(new_order, new_order['seller'].decode('hex'))

    def send_order(self, new_order): # action
        new_order['state'] = 'sent'
        self._db.orders.update({"id":new_order['id']}, {"$set":new_order}, True)
        new_order['type'] = 'order'
        self._transport.send(new_order, new_order['buyer'].decode('hex'))

    def receive_order(self, new_order): # action
        new_order['state'] = 'received'
        self._db.orders.update({"id":new_order['id']}, {"$set":new_order}, True)
        self._transport.send(new_order, new_order['seller'].decode('hex'))


    # Order callbacks
    def on_order(self, msg):

        state = msg.get('state')

        buyer = msg.get('buyer').decode('hex')
        seller = msg.get('seller').decode('hex')
        myself = self._transport._myself.get_pubkey()

        if not buyer or not seller or not state:
            self._log.info("Malformed order")
            return

        if not state == 'new' and not msg.get('id'):
            self._log.info("Order with no id")
            return

        # Check order state
        if state == 'new':
            if myself == buyer:
                self.create_order(seller, msg.get('text', 'no comments'))
            elif myself == seller:
                self._log.info(msg)
                self.accept_order(msg)
            else:
                self._log.info("Not a party to this order")

        elif state == 'cancelled':
            if myself == seller or myself == buyer:
                self._log.info('Order cancelled')
            else:
                self._log.info("Order not for us")

        elif state == 'accepted':
            if myself == seller:
                self._log.info("Bad subjects [%s]" % state)
            elif myself == buyer:
                # wait for confirmation
                self._db.orders.update({"id":msg['id']}, {"$set":msg}, True)
                pass
            else:
                self._log.info("Order not for us")
        elif state == 'paid':
            if myself == seller:
                # wait for  confirmation
                pass
            elif myself == buyer:
                self.pay_order(msg)
            else:
                self._log.info("Order not for us")
        elif state == 'sent':
            if myself == seller:
                self.send_order(msg)
            elif myself == buyer:
                # wait for confirmation
                pass
            else:
                self._log.info("Order not for us")
        elif state == 'received':
            if myself == seller:
                pass
                # ok
            elif myself == buyer:
                self.receive_order(msg)
            else:
                self._log.info("Order not for us")

        # Store order
        if msg.get('id'):
            if self.orders.find( {id:msg['id']}):
                self.orders.update({'id':msg['id']}, { "$set": { 'state':msg['state'] } }, True)
            else:
                self.orders.update({'id':msg['id']}, { "$set": { msg } }, True)

if __name__ == '__main__':
    seller = ECC(curve='secp256k1')
    class FakeTransport():
        _myself = ECC(curve='secp256k1')
        def add_callback(self, section, cb):
            pass
        def send(self, msg, to=None):
            print 'sending', msg
        def log(self, msg):
            print msg
    transport = FakeTransport()
    rep = Orders(transport)
    rep.on_order(order(None, transport._myself.get_pubkey(), seller.get_pubkey(), 'new', 'One!', ["dsasd", "deadbeef"]))
