#!/usr/bin/python
import sys, os, socket, time, signal

# Market Info
MY_MARKET_IP = "127.0.0.1" #socket.gethostbyname(socket.gethostname())
MY_MARKET_PORT = 12345

# Entangled Node Info
MY_NODE_PORT = 43251

# Specify a seed URI or you will be put into demo mode
SEED_URI = "tcp://seed.openbazaar.org:12345"
MY_NODE_FILE = "shop/local_nodes"

# Run in local test mode by default
MODE = "test"

# Store config file
STOREFILE = "ppl/default"

# Location of log directory
LOGDIR = "logs"

# number of nodes to create
SIZE = 4

def destroyNetwork(nodes):
    print 'Destroying Kademlia network...'
    i = 0
    for node in nodes:
        i += 1
        time.sleep(0.15)
        os.kill(node, signal.SIGTERM)
    print

def demoMode():
    demo_port = 47771
    demo_ip_prefix = "127.0.0."
    
    demo_nodes = []
    demo_storefiles = ["ppl/default","ppl/s_tec","ppl/genjix","ppl/novaprospekt"]
    
    try:
        # Primary Market - No SEED_URI specified
        print '** Creating seed node 1'
        os.spawnlp(os.P_WAIT,'touch','touch',LOGDIR+"/demo_node1.log")
        demo_nodes.append( os.spawnlp(os.P_NOWAIT, 'python2', 'python2', './node/tornadoloop.py',
                                      demo_storefiles[0], demo_ip_prefix+str(1),
                                      "--my_node_port="+str(demo_port), "--log_file="+LOGDIR+"/demo_node1.log", "--userid=1"))
        time.sleep(2)
        demo_port += 1
        
        # Demo Peer Market
        for num in range(2,SIZE+1):
            print '\n** Creating node %s' % num
            os.spawnlp(os.P_WAIT,'touch','touch',LOGDIR+"/demo_node%s.log"%num)
            demo_nodes.append( os.spawnlp(os.P_NOWAIT, 'python2', 'python2', './node/tornadoloop.py',
                                          demo_storefiles[(num-1)%len(demo_storefiles)], demo_ip_prefix + str(num),
                                          "--seed_uri=tcp://127.0.0.1:12345", "--my_node_port=" + str(demo_port), "--log_file=" + LOGDIR + "/demo_node%d.log"%num, "--userid=%d"%num))
            time.sleep(2)
            demo_port += 1
    except KeyboardInterrupt:
        '\ncancelled launch process'
        destroyNetwork(demo_nodes)
        sys.exit(1)
        
    print '\n\n---------------\nNetwork running\n---------------\n'
    # blocks until interrupt to shutdown nicely
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        destroyNetwork(demo_nodes)


# if executed directly, run the setup process
if __name__ == '__main__':

    if len(sys.argv) > 1:
        MODE = sys.argv[1]
    elif len(sys.argv) > 2:
        SEED_URI = "tcp://"+sys.argv[2]+":"+str(MY_MARKET_PORT)

    dir = os.path.dirname("./"+LOGDIR)
    try:
        os.stat(dir)
    except:
        os.mkdir(dir)   

    # seed mode to start a network from
    if (MODE == "seed"):
        os.spawnlp(os.P_WAIT,'touch','touch',LOGDIR+"/node.log")
        seed_node = os.spawnlp(os.P_NOWAIT, 'python2', 'python2', './node/tornadoloop.py',
                               STOREFILE, MY_MARKET_IP, "--my_node_port=" + str(MY_NODE_PORT), "--my_node_file=" + MY_NODE_FILE, "--log_file=" + LOGDIR + "/node.log", "--userid=1")
        
    # production mode initialization, connection to network
    elif (MODE == "production"):
        os.spawnlp(os.P_WAIT,'touch','touch',LOGDIR+"/node.log")
        production_node = os.spawnlp(os.P_NOWAIT, 'python2', 'python2', './node/tornadoloop.py',
                                     STOREFILE, MY_MARKET_IP, "--seed_uri=" + SEED_URI, "--my_node_port=" + str(MY_NODE_PORT), "--my_node_file=" + MY_NODE_FILE, "--log_file=" + LOGDIR + "/node.log", "--userid=1")    
    
    # demo mode with multiple running in local context
    else:
        demoMode()
