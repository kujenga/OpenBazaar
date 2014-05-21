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
import re
import threading


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect("/html/index.html")


class MarketApplication(tornado.web.Application):

    def __init__(self, store_file, my_market_ip, my_market_port, my_node_port, my_node_file, seed_uri, market_id):

        self.transport = CryptoTransportLayer(my_market_ip,
                                              my_market_port,
                                              market_id)
        self.transport.join_network(seed_uri)
        # TODO: would be nice to have persistent data storage, create a database if one doesn't exist
        dataStore = SQLiteDataStore() #'/shop/sites.sqlite')
        # TODO: need a way to cache more of these persistently and load each time
        if my_node_file == None:
            # finds IP addresses in the seed_uri
            seed_ip = re.search(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",seed_uri)
            if seed_ip == None:
                # if no IP address present, finds a text URL address
                seed_ip = re.search(r"[a-z]*\.[a-z]*\.[a-z]*",suri)
            knownNodes = [(seed_ip.group(0), my_node_port)]
        else:
            knownNodes = []
            f = open(my_node_file, 'r')
            lines = f.readlines()
            f.close()
            for line in lines:
                ipAddress, udpPort = line.split()
                knownNodes.append((ipAddress, int(udpPort)))
        #print("knownNodes for Entangled: "+" ".join(str(n) for n in knownNodes));
        self.node = entangled.node.EntangledNode(udpPort=my_node_port, dataStore=dataStore)
        # needs some entry point into the ring, see TODO above
        self.node.joinNetwork(knownNodes)
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


<<<<<<< HEAD
# Run this if executed directly
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("store_file",
                        help="You need to specify a user crypto file in `ppl/` folder")
    parser.add_argument("my_market_ip",
                        help="You need to specify an IP address for your market")
    parser.add_argument("-p", "--my_market_port", type=int, default=12345)
    parser.add_argument("-n", "--my_node_port", type=int, default=54321)
    parser.add_argument("-f", "--my_node_file", default='shop/nodes')
    parser.add_argument("-s", "--seed_uri")
    parser.add_argument("-l", "--log_file", default='node.log')
    args = parser.parse_args()

=======
def start_node(my_market_ip, my_market_port, seed_uri, log_file, userid):
>>>>>>> upstream/master
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s -  \
                                %(levelname)s - %(message)s',
                        filename=log_file)

<<<<<<< HEAD
    application = MarketApplication(args.store_file, args.my_market_ip,
                                    args.my_market_port, args.my_node_port, args.my_node_file, args.seed_uri)
=======
    application = MarketApplication(my_market_ip,
                                    my_market_port, seed_uri, userid)
>>>>>>> upstream/master

    error = True
    port = 8888
    while error and port < 8988:
        try:
            application.listen(port)
            error = False
        except:
            port += 1

    logging.getLogger().info("Started user app at http://%s:%s"
                             % (my_market_ip, port))

    # handle shutdown
    def shutdown(x, y):
        application.get_transport().broadcast_goodbye()
        sys.exit(0)
    try:
        signal.signal(signal.SIGTERM, shutdown)
    except ValueError:
        # not the main thread
        pass

    tornado.ioloop.IOLoop.instance().start()

# Run this if executed directly
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("my_market_ip")
    parser.add_argument("-p", "--my_market_port", type=int, default=12345)
    parser.add_argument("-s", "--seed_uri")
    parser.add_argument("-l", "--log_file", default='node.log')
    parser.add_argument("-u", "--userid", default=1)
    args = parser.parse_args()
    start_node(args.my_market_ip,
               args.my_market_port, args.seed_uri, args.log_file, args.userid)
