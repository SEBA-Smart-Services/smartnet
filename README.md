# SmartNet

SmartNet (formerly Ulysses) is a suite of communications, networking and security solutions for enabling smart building services.

## SmartNet secure network
Primarily, SmartNet is an IPsec VPN network for connecting registered Schnedier Electric systems to local Schneider Electric service teams and Performance Centres.

The network is arranged in a site-to-site [hub-and-spoke topology](http://www.ciscopress.com/articles/article.asp?p=606584&seqNum=3), with each local Performance Centre as local "hub". Remote access clients can connect using IKEv1 IPsec/L2TP, native to most operating systems.

### Client VPN configuration

 * [Linux](linux-ipsec-client.md) 
 * Non-Linux: For now, get started using the [Meraki Client VPN OS Configuration document](https://documentation.meraki.com/MX-Z/Client_VPN/Client_VPN_OS_Configuration). Better docs added as a TODO.

## SmartNet wireless mesh

SmartNet wireless mesh is an adhoc wireless mesh networking solution for faciliting intra-site communications across a broad geospatial area, where traditional wired networking infrastructure is too costly or not physically feasible.

Instructions for deploying a wireless mesh node can be found [here](batman_mesh_network/README.md).

## TODO:

* Documentation for remote access client for:
  - Windows
  - iOS
  - Android 
* Documentation for deploying a new node.
* Meraki Dashboard API integration with Medusa.


## Support or Contact

Having trouble or want to learn more? [contact support](mailto:admin@sebbqld.com) and we’ll help you sort it out.
