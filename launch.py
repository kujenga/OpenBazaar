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

def destroy_network(nodes):
    print 'Destroying Kademlia network...'
    i = 0
    for node in nodes:
        i += 1
        time.sleep(0.15)
        os.kill(node, signal.SIGTERM)
    print

def kill_some(nodes,amt):
    if amt < len(nodes):
        print 'killing %d nodes out of %d remaining' % (amt,len(nodes))
        from random import randint
        for i in range(0,amt):
            cur = nodes.pop(randint(0,len(nodes)-1))
            print'killing node %s' % cur
            os.kill(cur, signal.SIGTERM)
    elif amt == len(nodes):
        print 'killing all remaining %d nodes' % amt
        destroy_network(nodes)
    else:
        print 'impossible, only %d nodes exist' % len(nodes)

def respond_to_input(s,nodes):
    if s.lstrip().startswith("help"):
        print 'usage:'
        print 'help: displays the command options'
        print 'kill <number>: kills the specified number of nodes'
        print 'create <number>: creates the specified number of nodes'
        print 'destroy: destroys all nodes and quits the program'
    elif s.lstrip().startswith("kill"):
        try:
            num = int(s.split(" ")[1].strip())
        except:
            print 'Please provide command of form: kill <number>'
        print 'killing %d nodes' % num
        kill_some(nodes,num)
    elif s.lstrip().startswith("create"):
        try:
            num = int(s.split(" ")[1].strip())
        except:
            print 'Please provide command of form: create <number>'
        print 'creating %d nodes' % num
    elif s.lstrip().startswith("status"):
        for i,node in enumerate(nodes):
            print "node %d: %s" % (i+1,node)
    elif s.lstrip().startswith("destroy"):
        destroy_network(nodes)
    else:
        print 'Unrecognized command. Use \'help\' for more information'


def demo_mode():
    demo_port = 47771
    demo_ip_prefix = "127.0.0."
    
    demo_nodes = []
    demo_storefiles = ["ppl/default","ppl/s_tec","ppl/genjix","ppl/novaprospekt"]
    
    try:
        # Primary Market - No SEED_URI specified
        print '** Creating seed node 1'
        os.spawnlp(os.P_WAIT,'touch','touch',LOGDIR+"/demo_node1.log")
        demo_nodes.append( os.spawnlpe(os.P_NOWAIT, 'python2', 'python2', './node/tornadoloop.py',
                                      demo_storefiles[0], demo_ip_prefix+str(1),
                                       "--my_node_port="+str(demo_port), "--log_file="+LOGDIR+"/demo_node1.log", "--userid=1", os.environ))
        time.sleep(1)
        demo_port += 1
        
        # Demo Peer Market
        for num in range(2,SIZE+1):
            print '\n** Creating node %s' % num
            os.spawnlp(os.P_WAIT,'touch','touch',LOGDIR+"/demo_node%s.log"%num)
            demo_nodes.append( os.spawnlpe(os.P_NOWAIT, 'python2', 'python2', './node/tornadoloop.py',
                                           demo_storefiles[(num-1)%len(demo_storefiles)], demo_ip_prefix + str(num),
                                           "--seed_uri=tcp://127.0.0.1:12345", "--my_node_port=" + str(demo_port), "--log_file=" + LOGDIR + "/demo_node%d.log"%num, "--userid=%d"%num,
                                           os.environ))
            time.sleep(1)
            demo_port += 1
    except KeyboardInterrupt:
        '\ncancelled launch process'
        destroy_network(demo_nodes)
        sys.exit(1)

    time.sleep(1.75)
    print '\n\n---------------\nNetwork running\n---------------\n'
    print 'use \'help\' for more information\n'
    # blocks until interrupt to shutdown nicely

    try:
        while 1:
            s = raw_input('> ')
            respond_to_input(s,demo_nodes)
    except KeyboardInterrupt:
        pass
    finally:
        destroy_network(demo_nodes)
    

# if executed directly, run the setup process
if __name__ == '__main__':

    if len(sys.argv) > 1:
        # assigns a number to size if the demo and a string to the specified mode
        try:
            SIZE = int(sys.argv[1])
        except:
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
        demo_mode()
