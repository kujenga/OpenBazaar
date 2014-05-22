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

# for Entangled implementation
import entangled.node
from entangled.kademlia.datastore import SQLiteDataStore


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect("/html/index.html")


class MarketApplication(tornado.web.Application):

    def __init__(self, store_file, my_market_ip, my_market_port, my_node_port, my_node_file, seed_uri, market_id):
        import twisted.internet.reactor
        
        self.transport = CryptoTransportLayer(my_market_ip,
                                              my_market_port,
                                              market_id,
                                              store_file)
        self.transport.join_network(seed_uri)
        # TODO: should have persistent data storage, or create a database if one doesn't exist
        dataStore = SQLiteDataStore()
        known_nodes = self.known_entangled_nodes(my_node_file,seed_uri,my_node_port)
        # initializes node with specified port and an in-memory SQLite database
        self.node = entangled.node.EntangledNode(udpPort=my_node_port, dataStore=dataStore)
        # sjoins the Kademlia DHT network
        self.node.joinNetwork(known_nodes)

        self.market = Market(self.transport,self.node,store_file)

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
        twisted.internet.reactor.run()

    def get_transport(self):
        return self.transport

    # creates list of known node tuples either from node_file or the seed_uri
    def known_entangled_nodes(self,node_file,seed_uri,node_port):
        if node_file == None:
            if seed_uri == None:
                return None
            # finds IP addresses in the seed_uri
            seed_ip = re.search(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",seed_uri)
            if seed_ip == None:
                # if no IP address present, finds a text URL address
                seed_ip = re.search(r"[a-z]*\.[a-z]*\.[a-z]*",suri)
            knownNodes = [(seed_ip.group(0), 47771)]
        else:
            knownNodes = []
            f = open(node_file, 'r')
            lines = f.readlines()
            f.close()
            for line in lines:
                ipAddress, udpPort = line.split()
                knownNodes.append((ipAddress, int(udpPort)))
        print("known_nodes for Entangled: "+" ".join(str(n) for n in knownNodes));
        

def start_node(store_file, my_market_ip, my_market_port, my_node_port, my_node_file, seed_uri, log_file, user_id):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s -  \
                                %(levelname)s - %(message)s',
                        filename=log_file)

    application = MarketApplication(store_file, my_market_ip, my_market_port, my_node_port, my_node_file, seed_uri, user_id)

    error = True
    port = 8888
    while error and port < 8988:
        try:
            application.listen(port)
            error = False
        except:
            port += 1

    logging.getLogger().info("Started user app at http://%s:%s" % (my_market_ip, port))

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
    parser.add_argument("store_file",
                        help="You need to specify a user crypto file in `ppl/` folder")
    parser.add_argument("my_market_ip",
                        help="You need to specify an IP address for your market")
    parser.add_argument("-p", "--my_market_port", type=int, default=12345)
    parser.add_argument("-n", "--my_node_port", type=int, default=54321)
    parser.add_argument("-f", "--my_node_file", default=None)
    parser.add_argument("-s", "--seed_uri")
    parser.add_argument("-l", "--log_file", default='node.log')
    parser.add_argument("-u", "--userid", default=1)
    args = parser.parse_args()

    print(args)
    start_node(args.store_file, args.my_market_ip,
               args.my_market_port, args.my_node_port, args.my_node_file,
               args.seed_uri, args.log_file, args.userid)
