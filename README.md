# Fork Description

This is a fork for a final project for cs339 at Williams College. We have modified modified this system to use the Kademlia DHT so that one's site does not need to be locally hosted, but rather is hosted somewhere in the network as determined by the DHT. This eliminated the need for users to maintain a persistant connection to the network, maintaining a server, to remain active in the market. When users are offline, encrypted orders could be stored by others and then can be read by the owner of the site when they do connect. Community incentives, such as favorable rates with escrow figures and better reviews or ratings, could be associated with uptime and the amount of data that they are hosting so that there is an incentive for users to be connected when possible. Replication is also crucial with the ability to update and synchronize a site in response to changes from its owner.

We are using the Entangled inplementation of the Kademlia DHT design, which runs on the Twisted library. To have both the Entangled node and the market node running at the same time, the existing use of the TornadoIOLoop for the market node had to be modified. It now all runs of the Twisted Reactor with a TornadoLoop API ontop to allow for the continued function of the rest of the application without modification.

- Entangled: http://entangled.sourceforge.net
- Kademlia Specs: http://xlattice.sourceforge.net/components/protocol/kademlia/specs.html#replication
- Twisted: https://twistedmatrix.com/trac/
- Tornado: http://www.tornadoweb.org/en/stable/

==============

## running our fork and looking at processes

After your machine had been properly configured, you can run the program using the `launch.py` script in the top-level of the repository. This python script creates a simple CLI for the user to interact with, functionality is fairly simple to add by entending the functionality of the input listener. It currently supports killing a number of active nodes, viewing the active nodes, and creating new nodes, as well as shortcuts to the below terminal commands. Usage is viewable through the 'help' command while running the script.The 

To look at the status of the nodes on the machine, open a new terminal window and use one or both of the following commands.
- `ps aux | grep python`
 - This command displays all running python processes
 - used to check if the ndoes are running, or still running after an error and termination of the CLI
- `netstat -lp`
 - shows the port and IP address bindings of the local machine
 - if running in demo mode, you should see three ports in a `LISTEN` state for each process (Underscores represent actual numbers). One will be of the form `127.0.0._:12345` for the market interactions, another will be of the form `[::]:888_` for the browser connection, and the third will be of the form `*:4777_` for the entangled node connections on a local machine.
 - in demo mode, there will simply be just one set of these three port bindings, and the entangled node will be on port `4000`

==============

## Project folder purposes

- ecdsa: elliptic curve cryptography resources
- html: contains the actual website that the service uses, including a basic index.html and all the supporting files
- ident:
- msig: sx test files for playing with multisig. folder contains README with a link for more info
- node: contains the files that run the node on the client
 - files here handle all server interactions and communication with the outside world
- obelisk:
- ppl: Contains information on each user in the market. Each other user has their own file with nickname, keypair, and description. Can launch the server with any one of them
- pyelliptic: 
- shop: Contains the files for the user's website and homepage within the marketplace, as well as the entangled node locations.
- test: Contains code to test certain encryption functionality
- util: Contains a single file for bitcoin keypair generation. 


## Amazon EC2 nodes Quick Start

Make sure that the machine is running Ubuntu 12.04 or above with `lsb_release -d`

run `./configure.sh` which is included in the repository, answer the prompts with a `Y` as necessary.

When the process is completed, try to perform `./launch.py` and look to see what if any errors occur. If errors do occur, compare them with the different stages of the configure.sh file to see what might have gone wrong, or simply rectify them from the command line.

==============

OpenBazaar is a decentralized marketplace proof of concept. It is based off of the POC code by the darkmarket team and protected by the GPL.

See a demonstration of the Proof Of Concept here: https://www.youtube.com/watch?v=lHVqH8XO1Pk#t=86
Try out a demonstration at: http://seed.openbazaar.org:8888

This project is alpha and all feedback is welcome at: http://www.reddit.com/r/Bitcoin/comments/23y80c

Official site: http://openbazaar.org (currently a placeholder)

### IRC Chat
We are continually on IRC chat at #OpenBazaar on Freenode


## Features (Notional)
- Full market editor for management of items catalog
- Order management system
- Escrow-based transactions
- Arbiter management
- Private messaging
- Identity/Reputation system

## Project Status

All features are currently in alpha stage. Current functionality includes starting a connection to the distributed marketplace and viewing content in a browser. Transactions are not possible.

## Dependencies

**NOTE:** These dependencies are for reference, they do not need to be manually installed if the Quick Start guide is used.

- https://github.com/warner/python-ecdsa
- https://github.com/darkwallet/python-obelisk
- MongoDB

`pip install pyzmq`
`pip install tornado`
`pip install pyelliptic`
`pip install pymongo`
`pip install pycountry`

1. Install python-obelisk
2. git clone https://github.com/darkwallet/python-obelisk
3. python setup.py install


### MongoDB

OpenBazaar now uses MongoDB as the backend for storing persistent data. At the moment only orders are being tracked there, but this will be fleshed out ongoing. You will need to set up a MongoDB instance on your machine outside of this software and create a database called 'openbazaar'. There is no authentication or encryption configured, but I will be adding in support for this soon.

- Install MongoDB with OpenSSL
- Start MongoDB
- Create database named openbazaar

From command line:
`mongo`
`use openbazaar`


### OSX Users

For OSX there is a CLANG error when installing pyzmq but you can use the following command to ignore warnings:

`sudo ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future easy_install pyzmq`

### Issues with ./run_dev.sh
If you're getting errors saying `ZMQError: Can't assign requested address` then you probably need to bring up some loopback adapters for those
IPs higher than 127.0.0.1.

sudo ifconfig lo:1 127.0.0.2
sudo ifconfig lo:2 127.0.0.3
sudo ifconfig lo:3 127.0.0.4

## Identity Server

To get the identity server running for querying nicknames in the UI you need to start the identity server. From the base directory of the software run the following:

`python ident/identity.py`

### Tests
Install [behave](https://github.com/behave/behave) and run `behave` in the OpenBazaar folder. The tests themselves are located in the `features` folder.


## Artwork Contributions

![](https://github.com/OpenBazaar/OpenBazaar/blob/gh-pages/img/logo_alt1-b-h.png?raw=true)
contributed by Jacob Payne
![](http://i.imgur.com/WwPUXGS.png)
contributed by Dean Masley



## Screenshot

This screen shot looks horrible and is just a placeholder ATM. Designers wanted. Apply to brian@openbazaar.org if you're interested in helping out.

![Screen 1](http://i.imgur.com/qwByrqk.png)
![Screen 2](http://i.imgur.com/v3gRVgi.png)
![Screen 3](http://i.imgur.com/65eSjjz.png)
=======
