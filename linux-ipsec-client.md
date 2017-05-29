# Configuring Meraki Client VPN in Linux

You can try the official [Meraki Configuring Client VPN in Linux](https://documentation.meraki.com/MX-Z/Client_VPN/Configuring_Client_VPN_in_Linux) article for GUI based setup.
For terminal based configuration, see below.

## Install packages

Install the following packages:
 * strongswan
 * xl2tpd

For Arch Linux:
```
$ sudo pacman -S xl2tpd
```
Install [strongswan from the AUR](https://aur.archlinux.org/packages/strongswan/).

## Configure

4 configuration files need to be set up:
 1. `/etc/ipsec.conf`: This file contains the basic information to establish a secure IPsec tunnel to the VPN server. 
 2. `/etc/ipsec.secrets`: This file contains the PSK secret.
 3. `/etc/xl2tpd/xl2tpd.conf`: This file configures `xl2tpd` with the connection name, server IP address.
 4. `/etc/ppp/options.l2tpd.client`: This file configures `pppd`.
 
### ipsec.conf
 
Use the following config, replacing `yyy.yyy.yyy.yyy` with the Meraki node outside address and `my-unique-vpn-conn-name` with a connection name of your choice.
 
 ```
 $ sudo vim /etc/ipsec.conf
 
 conn %default
        ikelifetime=60m
        keylife=20m
        rekeymargin=3m
        keyingtries=1
        keyexchange=ikev1
        authby=secret
        ike=aes128-sha1-modp1024,3des-sha1-modp1024!
        esp=aes128-sha1-modp1024,3des-sha1-modp1024!

conn my-unique-vpn-conn-name
     keyexchange=ikev1
     left=%defaultroute
     auto=add
     authby=secret
     type=transport
     leftprotoport=17/1701
     rightprotoport=17/1701
     # set this to the outside IP address of your Meraki VPN node
     right=yyy.yyy.yyy.yyy
```

### ipsec.secrets

```
 $ sudo vim /etc/ipsec.secrets

: PSK "IPsec PSK secret goes here including quotation marks."
```

### xl2tpd.conf

Use the following config, replacing `yyy.yyy.yyy.yyy` with the Meraki node outside address and `my-unique-vpn-conn-name` with a connection name of your choice.

```
$ sudo vim /etc/xl2tpd/xl2tpd.conf

[lac my-unique-vpn-conn-name]
# set this to the outside IP address of your Meraki VPN node
lns = yyy.yyy.yyy.yyy
ppp debug = yes 
pppoptfile = /etc/ppp/options.l2tpd.client
length bit = yes
```

### options.l2tpd.client

Use the following config, replacing `meraki-username` and `meraki-password` with your client VPN username and password.

```
$ sudo vim /etc/ppp/options.l2tpd.client

ipcp-accept-local
ipcp-accept-remote
refuse-eap
require-pap
noccp
noauth
idle 1800
mtu 1410
mru 1410
defaultroute
usepeerdns
debug
connect-delay 5000
name meraki-username
password meraki-password
```

## Restart services

```
$ sudo systemctl restart strongswan
$ sudo systemctl restart xl2tpd
```

## Connect

Start the IPsec connection:

```
$ sudo ipsec up my-unique-vpn-conn-name
initiating Main Mode IKE_SA my-unique-vpn-conn-name[1] to yyy.yyy.yyyy.yyy
generating ID_PROT request 0 [ SA V V V V V ]
sending packet: from xxx.xxx.xxx.xxx[500] to yyy.yyy.yyyy.yyy[500] (212 bytes)
received packet: from yyy.yyy.yyyy.yyy[500] to xxx.xxx.xxx.xxx[500] (156 bytes)
...
connection 'my-unique-vpn-conn-name' established successfully
```

Start the L2TP connection:
```
$ su
# echo "c my-unique-vpn-conn-name" > /var/run/xl2tpd/l2tp-control
```

## Add routes

Check the tunnel has been created as an interface:
```
$ ip link
...
4: ppp0: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> mtu 1392 qdisc fq_codel state UNKNOWN mode DEFAULT group default qlen 3 link/ppp
```

Add a route to the VPN inside network through the ppp tunnel.
```
$ ip route add zzz.zzz.zzz.zzz/zzz dev ppp0
```

You should now have access to the Meraki node inside LAN.

## Disconnect
```
$ su
# echo "d my-unique-vpn-conn-name" > /var/run/xl2tpd/l2tp-control
# exit
$ sudo ipsec down my-unique-vpn-conn-name
closing CHILD_SA my-unique-vpn-conn-name...
...
IKE_SA [...] closed successfully
```

## References

 * [meraki_strongswan_notes](https://gist.github.com/psanford/42c550a1a6ad3cb70b13e4aaa94ddb1c) by @psanford.
 * [Openswan L2TP/IPsec VPN client setup](https://wiki.archlinux.org/index.php/Openswan_L2TP/IPsec_VPN_client_setup) on the Arch Linux Wiki.
