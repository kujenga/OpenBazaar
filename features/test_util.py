import json
import time
from multiprocessing import Process

from node.tornadoloop import start_node
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.websocket import websocket_connect
from pymongo import MongoClient


def ws_connect(node_index):
    port = str(node_to_ws_port(node_index))

    @gen.coroutine
    def client():
        client = yield websocket_connect('ws://localhost:%s/ws' % port)
        message = yield client.read_message()
        raise gen.Return(json.loads(message))

    return IOLoop.current().run_sync(client)


def ws_send_raw(port, string):
    @gen.coroutine
    def client():
        client = yield websocket_connect('ws://localhost:%s/ws' % port)
        message = yield client.read_message()
        client.write_message(json.dumps(string))
        message = yield client.read_message()
        raise gen.Return(json.loads(message))

    return IOLoop.current().run_sync(client)


def ws_send(node_index, command, params={}):
    port = str(node_to_ws_port(node_index))
    cmd = {'command': command,
           'id': 1,
           'params': params}
    ret = ws_send_raw(port, cmd)
    time.sleep(0.1)
    return ret


def create_nodes(context, num_nodes):
    proc = []
    for i in range(num_nodes):
        proc.append(Process(target=start_node,
                            args=('127.0.0.%s' % str(i+1),
                                  12345,
                                  None,
                                  'test%s.log' % str(i),
                                  i)))
        proc[i].start()
        time.sleep(1)
        settings_set_page(i)
    context.proc = proc


def create_connected_nodes(context, num_nodes):
    create_nodes(context, num_nodes)
    for i in range(num_nodes-1):
        ws_send(i, 'connect', {'uri': node_addr(i+1)})


def node_addr(node_index):
    return 'tcp://127.0.0.%s:12345' % str(node_index+1)


def node_to_ws_port(node_index):
    return node_index + 8888

def settings(market_id):
        MONGODB_URI = 'mongodb://localhost:27017'
        _dbclient = MongoClient()
        _db = _dbclient.openbazaar

        settings = _db.settings.find_one({'id':str(market_id)})
        return settings

def settings_set_page(market_id):
        # Connect to database
        MONGODB_URI = 'mongodb://localhost:27017'
        _dbclient = MongoClient()
        _db = _dbclient.openbazaar

        _db.settings.update({'id' : str(market_id)}, 
                            # {'$set': setting} , True)
                            {'$set': {'storeDescription':'Market %s' % str(market_id)}} , True)

def remove_settings(market_id):
        MONGODB_URI = 'mongodb://localhost:27017'
        _dbclient = MongoClient()
        _db = _dbclient.openbazaar

        _db.settings.remove({'id': '%s'%market_id})
