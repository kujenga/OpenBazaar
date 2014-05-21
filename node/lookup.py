import zmq
import logging

class QueryIdent:

    def __init__(self):
        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.REQ)

        # Point to OpenBazaar Identity server for now
        self._socket.connect("tcp://seed.openbazaar.org:5558")

        self._log = logging.getLogger(self.__class__.__name__)

    def lookup(self, user):
        self._socket.send(user)
        key = self._socket.recv()
        self._log.info("Lookup %s" % user)
        if key == "__NONE__":
            return None
        return key

if __name__ == "__main__":
    query = QueryIdent()
