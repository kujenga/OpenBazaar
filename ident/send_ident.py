import zmq
c = zmq.Context()
s = c.socket(zmq.PUSH)
s.connect("tcp://localhost:5557")

s.send("default", flags=zmq.SNDMORE)
s.send("03960478444a2c18b0cd82b461c2654fc3b96dd117ddd524558268be3044192b97".decode("hex"))
