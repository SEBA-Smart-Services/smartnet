## BATMAN MESH NETWORK SETUP

Instructions for setting up a simple batman mesh network, specifically for the hyrax PCP-105. If you run into any difficulties or require further details please refer to intellidesign user reference manual for hyrax PCP-105 (DOC: HYR03001).

### Setup
1. Connect power, antenna and ethernet cable (eth0) to device.
1. SSH into device (using PuTTY) through ethernet IP address.
    1. Ensure the fixed *ethernet network IP* of current device matches that of the one you are trying to connect to (see IP settings below for more details).
1. Change directories to the etc/config file (from PuTTY login type `cd ../etc/config`)
1. Type in the following commands to configure the batman-adv file (or manually change the values by using `vim batman-adv`, *see vim commands below for additional help*)
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
    1. `uci set batman-adv.bat0.ip=xxx.xxx.xxx.xxx` set the devices IP address for the mesh network
    1. `uci set batman-adv.bat0.mask=xxx.xxx.xxx.xxx` set the mask for the device (make sure it is the same for all devices)
    1. `uci set batman-adv.bat0.gw_mode=client` set to be either "server" or "client" depending on whether the particular device needs to be able to communicate with the internet (server) or not (client)
    1. `uci set batman-adv.bat0.enable=1`
1. Save settings and restart batman by:
    1. `uci commit`
    1. `sync`
    1. `/etc/init.d/batman-adv restart`
1. Verify changes have been made by checking the file `vim batman-adv` or running `ifconfig` and looking at the details in bat0 network.
1. 

### Testing connection
Once everything is connected you can test the mesh network by pinging devices on the network (requires at least two active devices on the network)

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

### Vim commands
Some basic vim commands:
  1. Press **ESC** to enter command mode
      1. `:w` to save changes
      1. `:q` to exit vim
      1. `:wq` to save and exit
  1. Press **i** to enter insert mode where you can start editing the program (should say --insert-- down the bottom of terminal)
  1. Do not press **ctrl+s** as this enters a "freeze" mode, if accidentally pressed use **ctrl+q** to unfreeze.
  1. use **dd** to delete a single line.

### Trouble shooting
If you can no longer access device through Ethernet or WIFI, try using serial (USB) to connect.
  1. Open up the centre compartment on top.
  1. Plug in microUSB.
      1. If device is unrecognised download latest driver for the device.
      1. In device manager under COM find which COM channel the device is talking through (i.e COM4).
  1. Connect to device through serial connection (check box in PuTTY).
      1. Host name will be whatever COM channel it was talking through.
