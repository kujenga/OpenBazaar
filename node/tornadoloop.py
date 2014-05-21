import sys
import argparse
import tornado.ioloop
import tornado.web
import tornado.ioloop
from zmq.eventloop import ioloop
ioloop.install()
from crypto2crypto import CryptoTransportLayer
from market import Market
from ws import WebSocketHandler
import logging
import signal

# for Entangled implementation
import entangled.node
from entangled.kademlia.datastore import SQLiteDataStore

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect("/html/index.html")


class MarketApplication(tornado.web.Application):

    def __init__(self, store_file, my_market_ip, my_market_port, my_node_port, seed_uri):

        self.transport = CryptoTransportLayer(my_market_ip,
                                              my_market_port,
                                              store_file)
        self.transport.join_network(seed_uri)
        # TODO: would be nice to have persistent data storage, create a database if one doesn't exist
        dataStore = SQLiteDataStore() #'/shop/sites.sqlite')
        # TODO: need a way to cache these persistently and load them each time, cannot be empty
        knownNodes = [()]
        self.node = entangled.node.EntangledNode(udpPort=my_node_port, dataStore=dataStore)
        # needs some entry point into the ring, see TODO above
        self.node.joinNetwork() #knownNodes)
        self.market = Market(self.transport,self.node)

        handlers = [
            (r"/", MainHandler),
            (r"/main", MainHandler),
            (r"/html/(.*)", tornado.web.StaticFileHandler, {'path': './html'}),
            (r"/ws", WebSocketHandler,
                dict(transport=self.transport, node=self.market))
        ]

        # TODO: Move debug settings to configuration location
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)

    def get_transport(self):
        return self.transport


# Run this if executed directly
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("store_file",
                        help="You need to specify a user \
                                crypto file in `ppl/` folder")
    parser.add_argument("my_market_ip")
    parser.add_argument("-p", "--my_market_port", type=int, default=12345)
    parser.add_argument("-n", "--my_node_port", type = int, default=54321)
    parser.add_argument("-s", "--seed_uri")
    parser.add_argument("-l", "--log_file", default='node.log')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s -  \
                                %(levelname)s - %(message)s',
                        filename=args.log_file)

    application = MarketApplication(args.store_file, args.my_market_ip,
                                    args.my_market_port, args.my_node_port, args.seed_uri)

    error = True
    port = 8888
    while error and port < 8988:
        try:
            application.listen(port)
            error = False
        except:
            port += 1

    logging.getLogger().info("Started user app at http://%s:%s"
                             % (args.my_market_ip, port))

    # handle shutdown
    def shutdown(x, y):
        application.get_transport().broadcast_goodbye()
        sys.exit(0)
    signal.signal(signal.SIGTERM, shutdown)

    tornado.ioloop.IOLoop.instance().start()
