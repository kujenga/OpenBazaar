# Fork Description

This is a fork for a final project for cs339 at Williams College. We intent to use a DHT to modify this system so that one's site does not need to be locally hosted, but rather is hosted somewhere in the network as determined by the DHT. THis allows for users to not need a persistant connection to the network to remain running. encrypted orders will be stored by others and then can be read by the owner of the site when they do connect. Community incentives, such as favorable rates with escrow figures and better reviews or ratings, could be associated with uptime and the amount of data that they are hosting so that there is an incentive for users to be connected when possible. Replication is also crucial with the ability to update and synchronize a site in respone to cnahges from its owner.

We intend to use the Entangled inplementation of the Kademlia DHT design, which runs on the Twisted library.

- Entangled: http://entangled.sourceforge.net
- Kademlia Specs: http://xlattice.sourceforge.net/components/protocol/kademlia/specs.html#replication
- Twisted: https://twistedmatrix.com/trac/

==============

## Project folder purposes

- ecdsa: elliptic curve cryptography resources
- html: contains the actual website that the service uses, including a basic index.html and all the supporting files
- ident:
- msig: sx test files for playing with multisig. folder contains README with a link for more info
- node: contains the files that run the node on the client
 - files here handle all server interactions and communication with the outside world
- obelisk:
- ppl: Contains information on other users in the market. each other user has their own file with nickname, keypair, and description.
 - uncertain as to who's private key is stored for each. our's to communicate with them? Are they just test users?
- pyelliptic: 
- shop: Contains the files for the user's website and homepage within the marketplace
- test: Contains code to test certain encryption functionality
- util: Contains a single file for bitcoin keypair generation. 

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

## Quick Start

These instructions download a VirtualBox image (Ubuntu Trusty) and use Vagrant to configure an OpenBazaar node inside the virtual environment. When the node is running, you can navigate to http://localhost:8888 on your local machine to access the client. This setup should take less than 10GB and about an hour. These instructions should include all necessary code for starting OpenBazaar.

1. This example is built on an Ubuntu Trusty host. Doesn't work from inside a virtual machine. 

    `sudo apt-get update`

    `sudo apt-get install virtualbox git vagrant`

2. clone openbazaar:

    `git clone https://github.com/kujenga/OpenBazaar.git`

    `cd OpenBazaar`
    
3. Set up vagrant: (this will take a while!)

    `vagrant up`

4. Log into the vagrant instance:

    `vagrant ssh`

5. Start the OpenBazaar node:

    `cd /vagrant && ./run_dev.sh`

6. Now return to your host and open your web browser to:

    `http://127.0.0.1:8888`


## Dependencies

**NOTE:** These dependencies are for reference, they do not need to be manually installed if the Quick Start guide is used.

- https://github.com/warner/python-ecdsa
- https://github.com/darkwallet/python-obelisk
- MongoDB

`pip install pyzmq`
`pip install tornado`
`pip install pyelliptic`
`pip install pymongo`

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


