# Node Folder

This folder contains the code necessary to run the node on the local machine

- crypto2crypto.py
- lookup.py
- multisig.py
- p2p.py
- reputation.py
- ws.py
- crypto2crypto.pyc market.py
- orders.py
 - handles all types of operations with orders, including a handler that processes incoming orders with a variety of methods
- protocol.py
 - A series of functions that return dictionary items with the specified parameters. these are then passed to other nodes as the mode of communication
- tornadoloop.py
 - runs the main loop that extends Application from tornado web server, handles the incoming requests