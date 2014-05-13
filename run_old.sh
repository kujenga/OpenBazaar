# Store config file
STOREFILE=ppl/default

# Location of log directory
LOGDIR=logs

# Specify a seed URI or you will be put into demo mode
#SEED_URI=tcp://127.0.0.1:12345
SEED_URI=

# Market Info
MY_MARKET_IP=127.0.0.1
MY_MARKET_PORT=12345

if which python2 2>/dev/null; then
    PYTHON=python2
else
    PYTHON=python
fi


if [ ! -d "$LOGDIR" ]; then
  mkdir $LOGDIR
fi
touch $LOGDIR/server.log

if [[ -n "$SEED_URI" ]]; then

	$PYTHON node/tornadoloop.py $STOREFILE $MY_MARKET_IP $SEED_URI > $LOGDIR//server.log &

else

	# Primary Market - No SEED_URI specified 
	$PYTHON node/tornadoloop.py $STOREFILE $MY_MARKET_IP > $LOGDIR/server.log &

	# Demo Peer Market
	sleep 1
	touch $LOGDIR/demo_peer.log
	$PYTHON node/tornadoloop.py $STOREFILE 127.0.0.2 tcp://$MY_MARKET_IP:$MY_MARKET_PORT > $LOGDIR//demo_peer.log &

fi

# TODO: Want to get rid of this
# Open the browser if -q is not passed:
if ! [ $1 = -q ]; then
    xdg-open http://localhost:8888
    xdg-open http://localhost:8889
fi
