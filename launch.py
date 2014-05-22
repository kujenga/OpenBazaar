#!/usr/bin/python
import sys, os
import socket
import time

# Market Info
MY_MARKET_IP = socket.gethostbyname(socket.gethostname())
MY_MARKET_PORT = 12345

# Entangled Node Info
MY_NODE_PORT = 43251

# Specify a seed URI or you will be put into demo mode
SEED_URI = "tcp://seed.openbazaar.org:12345"
MY_NODE_FILE = "shop/internal_nodes"

# Run in local test mode if not production
if len(sys.argv) > 1:
    MODE = "production"
    SEED_URI = "tcp://"+sys.argv[1]+":"+str(MY_MARKET_PORT)
else:
    MODE = "test"

# Store config file
STOREFILE = "ppl/default"

# Location of log directory
LOGDIR = "logs"

dir = os.path.dirname("./"+LOGDIR)
try:
    os.stat(dir)
except:
    os.mkdir(dir)   


if (MODE == "production"):
    # $PYTHON ident/identity.py # should find out what this does
    production_node = os.spawnlp(os.P_NOWAIT, 'python2', 'python2', './node/tornadoloop.py', STOREFILE, MY_MARKET_IP, "--seed_uri=" + SEED_URI, "--my_node_port=" + str(MY_NODE_PORT), "--my_node_file=" + MY_NODE_FILE, "--log_file=" + LOGDIR + "/node.log", "--userid=1")
    
elif (MODE == "seed"):
    seed_node = os.spawnlp(os.P_NOWAIT, 'python2', 'python2', './node/tornadoloop.py', STOREFILE, MY_MARKET_IP, "--my_node_port=" + str(MY_NODE_PORT), "--my_node_file=" + MY_NODE_FILE, "--log_file=" + LOGDIR + "/node.log", "--userid=1")

else:
    DEMO_NODE_PORT = 47771
    DEMO_IP_PRE = "127.0.0."

    demo_nodes = []
    demo_storefiles = ["ppl/default","ppl/s_tec","ppl/genjix","ppl/novaprospekt"]

    # Primary Market - No SEED_URI specified 
    demo_node_1 = os.spawnlp(os.P_NOWAIT, 'python2', 'python2', './node/tornadoloop.py',
                             demo_storefiles[0], DEMO_IP_PRE+str(1),
                             "--my_node_port="+str(DEMO_NODE_PORT), "--my_node_file="+MY_NODE_FILE, "--log_file="+LOGDIR+"/demo_node1.log", "--userid=1")
    
    # Demo Peer Market
    for num in range(2,5):
        time.sleep(2)
        DEMO_NODE_PORT += 1
        # $PYTHON node/tornadoloop.py $STOREFILE2 127.0.0.2 -s tcp://$PRIMARY_MARKET_IP:$MY_MARKET_PORT -n 47772 -f $MY_NODE_FILE -l $LOGDIR/demo_node2.log -u 2 &
        demo_nodes.append( os.spawnlp(os.P_NOWAIT, 'python2', 'python2', './node/tornadoloop.py',
                                      demo_storefiles[num-1], DEMO_IP_PRE + str(num),
                                      "--my_node_port=" + str(DEMO_NODE_PORT), "--my_node_file=" + MY_NODE_FILE, "--log_file=" + LOGDIR + "/demo_node%d.log"%num, "--userid=%d"%num))
