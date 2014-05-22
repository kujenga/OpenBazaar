# Market Info
MY_MARKET_IP=$(curl -s ifconfig.me)
MY_MARKET_PORT=12345
PRIMARY_MARKET_IP=127.0.0.1

# Entangled Node Info
MY_NODE_PORT=43251

# Specify a seed URI or you will be put into demo mode
SEED_URI=tcp://seed.openbazaar.org:12345
MY_NODE_FILE=shop/local_nodes

# Run in local test mode if not production
MODE=$1

# Store config file
STOREFILE=ppl/default

# Location of log directory
LOGDIR=logs

if which python2 2>/dev/null; then
    PYTHON=python2
else
    PYTHON=python
fi


if [ ! -d "$LOGDIR" ]; then
  mkdir $LOGDIR
fi

if [ $MODE == production ]; then

	
    #$PYTHON node/tornadoloop.py $STOREFILE $MY_MARKET_IP -s $SEED_URI -p $MY_MARKET_PORT -n $MY_NODE_PORT -l $LOGDIR/node.log &
    #$PYTHON ident/identity.py &
    $PYTHON node/tornadoloop.py $STOREFILE $MY_MARKET_IP -s $SEED_URI -p $MY_MARKET_PORT -n $MY_NODE_PORT -f $MY_NODE_FILE -l $LOGDIR/node.log -u 1 &

else

    # Primary Market - No SEED_URI specified 
    $PYTHON node/tornadoloop.py $STOREFILE $PRIMARY_MARKET_IP -n 47771 -f $MY_NODE_FILE -l $LOGDIR/demo_node1.log -u 1 &
    
    # Demo Peer Market
    sleep 2
    STOREFILE2=ppl/s_tec
    $PYTHON node/tornadoloop.py $STOREFILE2 127.0.0.2 -s tcp://$PRIMARY_MARKET_IP:$MY_MARKET_PORT -n 47772 -f $MY_NODE_FILE -l $LOGDIR/demo_node2.log -u 2 &
    
    sleep 2
    STOREFILE3=ppl/genjix
    $PYTHON node/tornadoloop.py $STOREFILE3 127.0.0.3 -s tcp://$PRIMARY_MARKET_IP:$MY_MARKET_PORT -n 47773 -f $MY_NODE_FILE -l $LOGDIR/demo_node3.log -u 3 &
    
    sleep 2
    STOREFILE4=ppl/novaprospekt
    $PYTHON node/tornadoloop.py $STOREFILE4 127.0.0.4 -s tcp://$PRIMARY_MARKET_IP:$MY_MARKET_PORT -n 47774 -f $MY_NODE_FILE -l $LOGDIR/demo_node4.log -u 4 &
    
fi
