# Active Folders

## About
ActiveFolders is a data transer tool desiged for ease of use within the research and HPC community.  ActiveFolders uses the '[science DMZ](http://delivery.acm.org/10.1145/2510000/2503245/a85-dart.pdf?ip=129.128.184.188&id=2503245&acc=ACTIVE%20SERVICE&key=FD0067F557510FFB%2EE7ED0E691902343F%2E4D4702B0C3E38B35%2E4D4702B0C3E38B35&CFID=603174431&CFTOKEN=16413392&__acm__=1417039609_daae7084437e0e1ea48a89053aa76ed7)' pattern to separate and optimise local-area network traffic and wide-area traffic. 

## Installation

ActiveFolders is installed by the Chef cookbooks found [here](https://github.com/cybera/activefolders-cookbook)

## API
We use Apiary to document our [API](http://docs.activefolders.apiary.io/).  Have a look!

A simple client illustrating use of the API is available for download [here](https://github.com/cybera/activefolders-tool)

## Features
#### Users
* Transfer files from user machines to HPC centres or other destinations
* Automatically detect and retrieve results from computations
* Pre-configured destinations; user only has to select destinations for their folder and add their credentials
* Supports ssh key authentication for destinations
* Token-based authentication
* Failed transfers are restartable

#### Admins
* Install Active Folders software on machines co-located with users and/or compute resources
* Users’ files are transferred to their DTN then to the DTN of their destination and finally to the destination
* DTNs can be part of a DMZ such that their WAN transfers aren’t impeded by enterprise firewalls
* Can configure list of available DTNs and destinations

#### Developers
* Modular transport system makes it easy to add support for additional protocols other than the default GridFTP and rsync


## Support
Questions?  Send an email to activefolders.project@gmail.com


## License and Authors
Copyright:: 2014, Paul Lu.

Licensed under the Apache License, Version 2.0 (the "License").
you may not use this file except in compliance with the License. 
You may obtain obtain a copy of the License at


    http://www.apache.org/licenses/LICENSE-2.0


Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and 
limitations under the License.
