import tornado.websocket
import threading
import logging
import json
import tornado.ioloop
import random
import protocol
import obelisk
import logging
import pycountry

class ProtocolHandler:
    def __init__(self, transport, node, handler):
        self.node = node
        self._transport = transport
        self._handler = handler

        # register on transport events to forward..
        transport.add_callback('peer', self.on_node_peer)
        transport.add_callback('peer_remove', self.on_node_remove_peer)
        transport.add_callback('page', self.on_node_page)
        transport.add_callback('all', self.on_node_message)

        # handlers from events coming from websocket, we shouldnt need this
        self._handlers = {
            "connect":          self.client_connect,
            "peers":          self.client_peers,
            "query_page":          self.client_query_page,
            "review":          self.client_review,
            "order":          self.client_order,
            "search":          self.client_search,
            "shout":          self.client_shout,
            "query_orders":	  self.client_query_orders,
            "query_products":	  self.client_query_products,
            "update_settings":	self.client_update_settings,
            "query_order":	self.client_query_order,
            "pay_order":	self.client_pay_order,
            "ship_order":	self.client_ship_order,
            "save_product":	self.client_save_product,
            "remove_product":	self.client_remove_product,
            "generate_secret":	self.client_generate_secret,
        }

        self._log = logging.getLogger(self.__class__.__name__)

    def send_opening(self):
        peers = self.get_peers()

        countryCodes = []
        for country in pycountry.countries:
          countryCodes.append({"code":country.alpha2, "name":country.name})

        settings = self.node.get_settings()

        message = {
            'type': 'myself',
            'pubkey': self._transport._myself.get_pubkey().encode('hex'),
            'peers': peers,
            'settings': settings,
            'countryCodes': countryCodes,
            'reputation': self.node.reputation.get_my_reputation()
        }

        self.send_to_client(None, message)

    # Requests coming from the client
    def client_connect(self, socket_handler, msg):
        self._log.info("Connection command: ", msg)
        self._transport.init_peer(msg)
        self.send_ok()

    def client_peers(self, socket_handler, msg):
        self._log.info("Peers command")
        self.send_to_client(None, {"type": "peers", "peers": self.get_peers()})

    def client_query_page(self, socket_handler, msg):
        self._log.info("Message: ", msg)
        pubkey = msg['pubkey'].decode('hex')
        self.node.query_page(pubkey)
        self.node.reputation.query_reputation(pubkey)

    def client_query_orders(self, socket_handler, msg):

        self._log.info("Querying for Orders")

        # Query mongo for orders
        orders = self.node.orders.get_orders()

        self.send_to_client(None, { "type": "myorders", "orders": orders } )

    def client_query_products(self, socket_handler, msg):

        self._log.info("Querying for Products")

        # Query mongo for products
        products = self.node.get_products()

        self.send_to_client(None, { "type": "products", "products": products } )

    # Get a single order's info
    def client_query_order(self, socket_handler, msg):



        # Query mongo for order
        order = self.node.orders.get_order(msg['orderId'])

        self.send_to_client(None, { "type": "orderinfo", "order": order } )


    def client_update_settings(self, socket_handler, msg):
        self._log.info("Updating settings: %s" % msg)

        self.send_to_client(None, { "type": "settings", "values": msg })

        # Update settings in mongo
        self.node.save_settings(msg['settings'])

    def client_save_product(self, socket_handler, msg):
        self._log.info("Save product: %s" % msg)

        # Update settings in mongo
        self.node.save_product(msg)

    def client_remove_product(self, socket_handler, msg):
        self._log.info("Remove product: %s" % msg)

        # Update settings in mongo
        self.node.remove_product(msg)

    def client_pay_order(self, socket_handler, msg):

        self._log.info("Marking Order as Paid: %s" % msg)

        # Update order in mongo
        order = self.node.orders.get_order(msg['orderId'])

        # Send to exchange partner
        self.node.orders.pay_order(order)

    def client_ship_order(self, socket_handler, msg):

        self._log.info("Shipping order out: %s" % msg)

        # Update order in mongo
        order = self.node.orders.get_order(msg['orderId'])

        # Send to exchange partner
        self.node.orders.send_order(order)

    def client_generate_secret(self, socket_handler, msg):

      new_secret = self.node.generate_new_secret()
      self.send_opening()


    def client_order(self, socket_handler, msg):
        self.node.orders.on_order(msg)

    def client_review(self, socket_handler, msg):
        pubkey = msg['pubkey'].decode('hex')
        text = msg['text']
        rating = msg['rating']
        self.node.reputation.create_review(pubkey, text, rating)

    def client_search(self, socket_handler, msg):
        self._log.info("[Search] %s"% msg)
        response = self.node.lookup(msg)
        if response:
            self._log.info(response)
            self.send_to_client(*response)

    def client_shout(self, socket_handler, msg):
        self._transport.send(protocol.shout(msg))

    # messages coming from "the market"
    def on_node_peer(self, peer):
        self._log.info("Add peer")

        response = {'type': 'peer',
                    'pubkey': peer._pub.encode('hex')
                              if peer._pub
                              else 'unknown',
                    #'nickname': peer.
                    'uri': peer._address}
        self.send_to_client(None, response)

    def on_node_remove_peer(self, msg):
        self.send_to_client(None, msg)

    def on_node_page(self, page):
        self.send_to_client(None, page)

    def on_node_message(self, *args):
        first = args[0]
        if isinstance(first, dict):
            self.send_to_client(None, first)
        else:
            self._log.info("can't format")

    # send a message
    def send_to_client(self, error, result):
        assert error is None or type(error) == str
        response = {
            "id": random.randint(0, 1000000),
            "result": result
        }
        if error:
            response["error"] = error
        self._handler.queue_response(response)

    def send_ok(self):
        self.send_to_client(None, {"type": "ok"})

    # handler a request
    def handle_request(self, socket_handler, request):
        command = request["command"]
        if command not in self._handlers:
            return False
        params = request["params"]
        # Create callback handler to write response to the socket.
        handler = self._handlers[command](socket_handler, params)
        return True

    def get_peers(self):
        peers = []
        for uri, peer in self._transport._peers.items():
            peer_item = {'uri': uri}
            if peer._pub:
                peer_item['pubkey'] = peer._pub.encode('hex')
            else:
                peer_item['pubkey'] = 'unknown'
            peers.append(peer_item)

        return peers

class WebSocketHandler(tornado.websocket.WebSocketHandler):

    # Set of WebsocketHandler
    listeners = set()
    # Protects listeners
    listen_lock = threading.Lock()

    def initialize(self, transport, node):
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.info("Initialize websockethandler")
        self._app_handler = ProtocolHandler(transport, node, self)
        self.node = node
        self._transport = transport

    def open(self):
        self._log.info('Websocket open')
        self._app_handler.send_opening()
        with WebSocketHandler.listen_lock:
            self.listeners.add(self)
        self._connected = True

    def on_close(self):
        self._log.info("websocket closed")
        disconnect_msg = {'command': 'disconnect_client', 'id': 0, 'params': []}
        self._connected = False
        self._app_handler.handle_request(self, disconnect_msg)
        with WebSocketHandler.listen_lock:
            self.listeners.remove(self)

    def _check_request(self, request):
        return request.has_key("command") and request.has_key("id") and \
            request.has_key("params") and type(request["params"]) == dict
            #request.has_key("params") and type(request["params"]) == list

    def on_message(self, message):

        self._log.info('Message: %s' % message)

        try:
            request = json.loads(message)
        except:
            logging.error("Error decoding message: %s", message, exc_info=True)

        # Check request is correctly formed.
        if not self._check_request(request):
            logging.error("Malformed request: %s", request, exc_info=True)
            return
        if self._app_handler.handle_request(self, request):
            return

    def _send_response(self, response):
        if self.ws_connection:
            self.write_message(json.dumps(response))
        #try:
        #    self.write_message(json.dumps(response))
        #except tornado.websocket.WebSocketClosedError:
        #    logging.warning("Dropping response to closed socket: %s",
        #       response, exc_info=True)

    def queue_response(self, response):
        ioloop = tornado.ioloop.IOLoop.instance()
        def send_response(*args):
            self._send_response(response)
        try:
            # calling write_message or the socket is not thread safe
            ioloop.add_callback(send_response)
        except:
            logging.error("Error adding callback", exc_info=True)
