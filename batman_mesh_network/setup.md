# SmartNet wireless mesh node setup

These instructions take new users through the process of setting up the wireless mesh network using BATMAN. The simple batman mesh network, was created for the hyrax PCP-105 running OpenWrt version xxxx. If you run into any difficulties or require further details please refer to intellidesign user reference manual for hyrax PCP-105 (DOC: HYR03001).

## OpenWrt Device

### Basic Setup
1. Connect power (DC power supply at least 3W), antenna and ethernet cable (eth0) to device.
1. SSH into device (using PuTTY) either through ethernet or wifi (any network changes made to the current connection will result in a loss in connection)
    1. If connecting through ethernet, plug the ethernet cable into either eth0 or eth1 on the hyreax device. Through putty connect to the  default IP address which is 192.168.1.1. The username and password for the device are root and openwrt respectively.
        1. Ensure the fixed *ethernet network IP* of current device matches that of the one you are trying to connect to (see IP settings below for more details).
    1. If using Wifi connect network ID `Intellidesign.FP2`, the password is `MyPASSWORD`, the default wifi IP to use for putty is 192.168.2.1. Similarly to above accept the authentication key and then password and username.
        1. Deafult IP can be used to access web config user interface through any web browser. login details are `root` and the password is `operwrt`
    1. An alternative method is connecting through USB, please refer to hyrax manual for more information.

1. Once connected to the device it is a good idea to change the default network values, this can be done through either UCI or the web UI.
    1. Using the command line you can either type in the commands directly or edit file, however once the files have been updated you will need to reboot the device.
1. Change directories to the *"etc/config"* file (from PuTTY login type `cd ../etc/config`).
1. To update the lan IP address go vim into the **network** file and under 'lan' section update the following fields
        ```
        option ipaddr '192.168.1.221' (Set to desired IP which should be unique for network)
        option netmask '255.255.255.0' (Set to desired subnet, should be same for all devices)
        ```
    1. NOTE: If you are connected via ethernet to the router once you save and reboot you wont be able to access the router, you will need to update the putty config and possibly update your own fixed IP depending on choice of IP. Save the changes made then from the command line type:
    ```
    sync
    /etc/init.d/network restart
    ```
    1. We do not need to worry about changing the wireless section as once the changes made later on in this setup the wireless option will no longer be available.
1. Next we will need to update the password (and username if desired)
    
### Configure batman-adv using UCI
Next we are going to configure the batman mesh network that the routers will communicate over. We will do this part using UCI commands however an easier method may be to manually change the file contents by using `vim batman-adv` and changing the corresponding settings

1. Type in the following commands to configure the *"batman-adv"* file.
    1. `uci set batman-adv.bat0=mesh`
    1. `uci set batman-adv.bat0.mesh_iface=wlan0`
    1. `uci set batman-adv.bat0.ap_isolation=0`
    1. `uci set batman-adv.bat0.bonding=0`
    1. `uci set batman-adv.bat0.fragmentation='1'`
    1. `uci set batman-adv.bat0.gw_sel_class='20'`
    1. `uci set batman-adv.bat0.orig_interval`
    1. `uci set batman-adv.bat0.bridge_loop_avoidance='0'`
    1. `uci set batman-adv.bat0.hop_penalty='15'`
    1. `uci set batman-adv.bat0.isolation_mark='0x00000000/0x00000000'`
    1. `uci set batman-adv.bat0.routing_algo='BATMAN_IV'`
    1. `uci set batman-adv.bat0.aggregated_ogms='1'`
    1. `uci set batman-adv.bat0.gw_bandwidth='10000'`
    1. `uci set batman-adv.bat0.ip=xxx.xxx.xxx.xxx` set the devices IP address for the mesh network (needs to be unique.
    1. `uci set batman-adv.bat0.mask=xxx.xxx.xxx.xxx` set the mask for the device (make sure it is the same for all devices).
    1. `uci set batman-adv.bat0.gw_mode=client` set to be either "server" or "client" depending on whether the particular device needs to be able to communicate with the internet (server) or not (client).
    1. `uci set batman-adv.bat0.enable=1`
1. Save settings and restart batman by:
    1. `uci commit`
    1. `sync`
    1. `/etc/init.d/batman-adv restart`
1. Verify changes have been made by checking the file `vim batman-adv` or running `ifconfig` and looking at the details in bat0 network.

### Configure Wireless Interface
Now that the batman configuration has been set we need to update a few files on the device.

1. First edit the *"wireless"* folder by editing using vim `vim wireless`.
    1. Under the ***config wifi-device*** section change 'wlan0' to 'radio0' and set up as follows.
        ```
            option type 'mac80211'
            option path 'pci0000:00/0000:00:17.0/0000:01:00.0'
            list ht_capab 'SHORT-GI-20'
            list ht_capab 'SHORT-GI-40'
            list ht_capab 'DSSS_CCK-40'
            option htmode 'HT40'
            option disabled '0'
            option channel '9'
            option hwmode '11g'
            option txpower '22'
            option country 'AU'
        ```
    1. in the next section (***config wifi-iface***) make the following changes
        ```
        config wifi-iface
            option device 'radio0' (needs to match ***config wifi-device***)
            option ifname 'mesh0'
            option network 'mesh' (can be called with whatever you want as long as they match up with all devices on mesh and network file)
            option mode 'adhoc'
            option ssid 'mesh' (can be called whatever you want as long as they match up with all devices on mesh)
            option bssid '02:CA:FE:CA:CA:40' (Can also be chosen but needs to be either numbers of letters between a and f)
            option encrytion 'none'
            option mcast_rate '18000'
        ```
    1. Save changes and exit
1. Now edit the *"network"* file and add the following configurations:
    ```
    config interface 'loopback'
        option ifname 'lo'
        option proto 'static'
        option ipaddr '127.0.0.1'
        option netmask '255.0.0.0'
        
    config interface 'mesh'
        option mtu '1532'
        option proto 'none
        option mesh 'mesh0'
    ```
1. We also need to create a bridge network on each router to allow for communications between the mesh and the outside. A bridge network creates a join between 2 networks which in this case will be between the batman network created earlier and the lan network already present on the routers. To create this bridge add the following configs to the *"network"* file.
    ```
    config globals 'globals'
        option ula_prefix 'fd73:8606:3736::/48
        
    config interface 'lan'
        option proto 'static'
        option gateway '192.168.1.1'
        option dns '8.8.8.8'
        option ifname 'eth0 bat0'
        option type 'bridge
    ```
1. Save all settings, restart network and batman-adv:
    ```
    sync
    /etc/init.d/network restart
    /etc/init.d/batman-adv restart
    ```
    
### Sample Configuration

With the configuration setup complete the files should look similar to the following.

#### /etc/config/network:
    config interface 'loopback'
        option ifname 'lo'
        option proto 'static'
        option ipaddr '127.0.0.1'
        option netmask '255.0.0.0'

    config globals 'globals'
            option ula_prefix 'fd73:8606:3736::/48'

    config interface 'lan'
            option proto 'static'
            option ipaddr 'xxx.xxx.xxx.xxx' (Set to desired IP should be unique for network)
            option netmask 'xxx.xxx.xxx.xxx' (Set to desired subnet, should be same for all devices)
            option gateway 'xxx.xxx.xxx.xxx' (Set to gateway for network)
            option dns 'xxx.xxx.xxx.xxx' (Set to network domain name server)
            option ifname 'eth0 bat0'
            option type 'bridge'

    config interface 'mesh'
            option mtu '1532'
            option proto 'none'
            option ifname 'mesh0'

#### /etc/config/system:
    config system
        option hostname 'ChosenHostName' (Name set by the user)
        option zonename 'Australia/Brisbane'
        option timezone 'AEST-10'
        option conloglevel '8'
        option cronloglevel '8'

    config timeserver 'ntp'
            list server '0.au.pool.ntp.org'
            list server '1.au.pool.ntp.org'
            list server '2.au.pool.ntp.org'
            list server '3.au.pool.ntp.org'
            option enabled '1'
            option enable_server '0'

#### /etc/config/wireless:
    config wifi-device 'radio0'
        option type 'mac80211'
        option path 'pci0000:00/0000:00:17.0/0000:01:00.0'
        list ht_capab 'SHORT-GI-20'
        list ht_capab 'SHORT-GI-40'
        list ht_capab 'DSSS_CCK-40'
        option htmode 'HT40'
        option disabled '0'
        option channel '9'
        option hwmode '11g'
        option txpower '22'
        option country 'AU'

    config wifi-iface
        option device 'radio0'
        option ifname 'mesh0'
        option network 'mesh'
        option mode 'adhoc'
        option ssid 'ChosenSSID' (SSID set by user)
        option bssid 'xx:xx:xx:xx:xx:xx' (BSSID created by user)
        option encryption 'none'
        option mcast_rate '18000'

#### /etc/config/batman-adv:
    config mesh 'bat0'
            option mesh_iface 'mesh0'
            option ap_isolation '0'
            option bonding '0'
            option fragmentation '1'
            option gw_mode 'client'
            option gw_sel_class '20'
            option orig_interval '1000'
            option bridge_loop_avoidance '1'
            option hop_penalty '255'
            option isolation_mark '0x00000000/0x00000000'
            option routing_algo 'BATMAN_IV'
            option aggregated_ogms '0'
            option gw_bandwidth '10000'
            option ip 'xxx.xxx.xxx.xxx' (IP used for batman network)
            option mask 'xxx.xxx.xxx.xxx' (Subnet masked used for batman network, should be same for all devices)
            option enable '1'


### Testing connection
Once everything is connected you can test the mesh network by pinging devices on the network (requires at least two active devices on the network).
1. Note down the devices IP addresses from earlier.
1. SSH into the device you wish to ping from (needs to be through ethernet as WIFI will no longer be available).
1. In the terminal type `ping x` where x is the IP address of the device you wish to talk to
    1. The terminal should start displaying statistics on how long the connection took along with other details.
    1. Sometimes there is high packet loss so only a few packets will get a response.
    1. To stop sending packets press **ctrl+c**, the terminal will output an overall statistics on the transmission.
1. A seperate way to test the connect is to use trace route (i.e. `traceroute x` where x is the IP address).
    1. This will show the path taken to reach the device you are trying to communicate with.
    1. \* means unresponsive and !H  means unreachable.
1. If there is no response check the antena on both devices are connected properly, if it is then double check your configuration set up on the device. If it is still not working please refer to the document mentioned at the top or visit the following link [BATMAN MESH NETWORK](https://www.open-mesh.org/projects/batman-adv/wiki/Batman-adv-openwrt-config).

### IP settings
The following explains how to check your IP in a windows environment
1. Open command terminal by searching for cmd in start menu and clicking *cmd.exe*
1. In cmd window type `ipconfig` and look at IPv4 address under the ethernet section.
    1. The network IP will depend on the subnet mask. If the IP is 192.168.20.10 and the mask is 255.255.255.0 then the network IP will be 192.168.20.0. If the mask was 255.255.0.0 then the network IP will be 192.168.0.0.
    1. To change the ethernet IP:
        1. Go to the network and sharing centre (right-click the internet icon in the bottom right).
        1. Select *change adaptor settings* in the left hand panel.
        1. Right-click Local area network and select properties.
        1. Double click IPv4.
        1. Select use the following IP address and use a custom IP that has the same network IP and subnet mask (the custom part of the address can take any number between 1 and 254 as long as it doesn't conflict with any other device on the network).

### Trouble shooting
If you can no longer access device through Ethernet or WIFI, try using serial (USB) to connect.
  1. Open up the centre compartment on top.
  1. Plug in microUSB.
      1. If device is unrecognised download latest driver for the device.
      1. In device manager under COM find which COM channel the device is talking through (i.e COM4).
  1. Connect to device through serial connection (check box in PuTTY).
      1. Host name will be whatever COM channel it was talking through.
