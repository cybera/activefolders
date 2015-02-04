### January 2015
First public release.  Not intended for production service

* Users
  * Transfer files from user machines to HPC centres or other destinations
  * Automatically detect and retrieve results from computations
  * Pre-configured destinations; user only has to select destinations for their folder and add their credentials
  * Supports ssh key authentication for destinations
  * Token-based authentication
  * Failed transfers are restartable

* Admins
  * Install Active Folders software on machines co-located with users and/or compute resources
  * Users’ files are transferred to their DTN then to the DTN of their destination and finally to the destination
  * DTNs can be part of a DMZ such that their WAN transfers aren’t impeded by enterprise firewalls
  * Can configure list of available DTNs and destinations

* Developers
  * Modular transport system makes it easy to add support for additional protocols other than the default GridFTP and rsync
