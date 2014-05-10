# Planned extensions for our final project

## General Ideas

 * Using replication to create reliability
 * Replicate an encrypted version of the local page across several other machines. A user can login to their account and operate their specific site within the marketplace without acess to their specific server, making the homepages less linked to specific machines which must be kept running.
  * Use a solution similar to BitTorrent where users agree to host a certain amount of data, and the client accesses the necessary pieces from one of a variety of sources when they are trying to go to a certain site.
  * Data stored by the nodes but owned by others would be encrpyted and anonymized, so each node would have no knowledge of what it was hosting, just an alloted amount of encrypted data.
  * People agree to host data in return for certain community incentives in the marketplace, such as lower arbitration fees or higher visibility in searches.
 * Could use certain parts of Tor to pass information around, e.g. hidden services
  * Don't want this to be limited to the Tor browser though, as that greatly limits exposure and access for the public
 * If a node goes offline, all data sent to it is cached in other servers, and when it or its replacement with the same "id" comes back on line, a request for all updates is propogated throughout the network
  * would need to use crytographic techniques to ensure that the reappeared node is in fact who they claim to be.

### Shared Hosting
 * each site has an associated index of places where the files can be hosted. The entire site, or each page of the site is compressed in a zip file. they are either replicated or divided into pieces to ensure that there are multiple possible sources from which to get the site.
 * Sites need to be divided up into slices that can be distributed and load balanced around the network
  * each slice can have associated statistics to ensure that it has adequate replication.
  * The "host" for the site has control over it, and timestamped updates are pushed out to the network if slices need to be updated.
  * a checksum or other hashing device can be used to ensure that the slices match the most recent version of the site.
 * users agree to host a certain amount of data by default, and then they respond to requests by sending back certain slices of data, of which they have no knowledge of the function.
  * the data they host is meaningless on its own
 * could use something similar to Bullet, discussed in class, to keep sites from hanging if they can't load the last bit necessary. build the rest of the data from what's already received
 * periodic updates pushed through the network through multicast. possibly use encryption in a way that the checksums or a hash of the slices act as private key to decode the pushed update
  * this prevents people who do not need to know about the update from understanding it
  * if the update can be interpreted, it is applied to the slice
  * updates could be in the form of a diff between the old and new, allowing for compression of the updates

### Incentives for cooperation
 * Escrow users who act as intermediaries charge a nomial fee for their services
 * that fee can be affected by how much data the users host. If they host nothing, maybe the rate is 2%, and if they host 3X what they have on the network, then maybe the rate goes down to 1%, following some formula that asymptotically approaches the lowest acceptable rate, maybe around 0.5%
 * in this way, there will be lots of users financially incentivized to host data, ensuring adequate replication for all sites across the network

### Search

 * Could implement an optional functionality that allows nodes to either be included in the search process through their active participation, or they can opt out to keep their site out of the results of the search
 * could implement search across the network in a way similar to Gnutella, ensuring anonymity of the end clients
  * branches out among the nodes like a tree traversal
 * use a TTL or max depth to prevent requests from flooding the network for long periods of time

### System Resiliance

 * making sure that single bad nodes cannot do malicious things
  * keeping community ratings of nodes with the intermediary entities, although that might be a burden on keeping security and implementing anonymity.
  * could have a blacklist of nodes that 

### Testing methods and metrics
 * ability to stand up to a network-wide shutdown
 * e.g. what happens if some entity is able to shutdown 10% of the nodes, or 20%, or even 50%?
 * how much replication is needed to ensure all or nearly all sites are maintained in a distrbuted way?