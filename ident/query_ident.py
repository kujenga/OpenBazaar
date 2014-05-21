import zmq
c = zmq.Context()
s = c.socket(zmq.REQ)
s.connect("tcp://seed.openbazaar.org:5558")
s.send("default")
key = s.recv()

if key == "__NONE__":
    print "Invalid nick"
else:
    print key.encode("hex")
