# Remote testing using SSH reverse tunnel over 3G connection

## Overview
Testing the mesh stability can be tedious if the routers are spread across a large geospatial area.
If a router drops off the mesh, it may require a long walk/drive to physically plug in and troubleshoot.
During FATs and SATs, it may be useful to create a temporary 3G internet connection on a router and configure remote terminal access.
There are a number of remote access methods, such as a persistent IPsec (using Strongswan) or OpenVPN to a VPN server.
In this example, we will set up a persistent reverse ssh tunnnel to an internet connected ssh server.

This is about 1 hours work, comprising of the following steps:
1. Configure the 3G connection on the routers.
2. Create and configure the ssh server.
3. Create public-private ssh keys for the routers to authenticate with the ssh server.
4. Test reverse ssh tunnel from router to ssh server
5. Create persistent reverse ssh tunnel on routers using autossh and init script

## Configure 3G connection on router
1. Insert SIM card as per hardware documentation.
2. ssh onto the router and configure the network interface, for example, for an Optus pre-paid 4G SIM card:

  ```
  # vim /etc/config/network
  
  ...
  config interface 'ppp0'
        option interface 'ppp0'
        option proto '3g'
        option device '/dev/ttyUSB3'
        option service 'umts'
        option apn 'connect'
        option ipv6 'auto'
  ...
  ```
  
Most of these settings should work for any Australian SIM card, just modify the APN option to suit the vendor.
  
3. Reboot
4. ssh back in and check internet connection, eg `ping google.com`. If no connection, check `logread` for hints, for example, the following output indicates a connection is established but the APN/authentication is incorrect and the provider terminates:

  ```
  Wed Sep  6 17:43:02 2017 daemon.info pppd[22863]: Serial connection established.
  Wed Sep  6 17:43:02 2017 kern.info kernel: [ 2639.526785] 3g-ppp0: renamed from ppp0
  Wed Sep  6 17:43:02 2017 daemon.info pppd[22863]: Using interface 3g-ppp0
  Wed Sep  6 17:43:02 2017 daemon.notice pppd[22863]: Connect: 3g-ppp0 <--> /dev/ttyUSB3
  Wed Sep  6 17:43:04 2017 daemon.notice pppd[22863]: Modem hangup
  Wed Sep  6 17:43:04 2017 daemon.notice pppd[22863]: Connection terminated.
  Wed Sep  6 17:43:05 2017 daemon.info pppd[22863]: Exit.
  Wed Sep  6 17:43:05 2017 daemon.notice netifd: Interface 'ppp0' is now down
  ```
  
  The following command will verify if a connection can be established with the provider:
  
  ```
  # gcom -d /dev/ttyUSBx
  ```
  
  For more troubleshooting steps, visit the [OpenWrt documentation on 3G/UMTS](https://wiki.openwrt.org/doc/recipes/3gdongle#debugging_signal_strength_issues).

## Deploy the ssh server
An internet accessible SSH server is required for each router to establish a persistent reverse SSH tunnel with. An AWS EC2 instance can be deployed and configured as an SSH server in under 30 minutes. The example EC2 instance has the following configuration:
- Instance type: t2.nano, the smallest and cheapest instance to run (at time of writing AU$0.008/hr, 0.5GB memory, 1vCPU)
- OS: Arch Linux, nice and lightweight, can easily run on t2.nano. Standard Ubuntu will work too but is much more resource heavy.

1. If using Arch Linux, deploy the [AMI from here](https://www.uplinklabs.net/projects/arch-linux-on-ec2/). If using a standard AWS image, such as Ubuntu, select it from the first page of the new EC2 instance wizard.
2. Follow the EC2 instance wizard, selecting the desired instance type (eg t2.nano).
3. Download SSH keys when prompted and keep safe.
4. Assign an elastic IP address to the server.
5. Configure EC2 Security Group. For security, the SSH port will be changed from default 22 to a free port of your choice, eg 12206. Modify the security group to allow the additional incoming TCP port for ssh. Each reverse tunnel from the routers will need to be proxied through to another TCP port. For example, the range TCP 15001-15010 for 10 routers, open these incoming ports too.
6. Once the EC2 instance is running, SSH onto the server:

  ```
  # Arch Linux
  ssh -i [your private key] root@[your elastic IP address]
  # Ubuntu
  ssh -i [your private key] ubuntu@[your elastic IP address]
  ```
  
  or PuTTY equivalent on Windows.
7. Modify the sshd_config as follows:

```
  # vim /etc/ssh/sshd_config
  
  #  to accept connections from your non default port
  Port 12206
  # disable password authentication and force public key authentication
  PasswordAuthentication no
  PubkeyAuthentication yes
  # to terminate ssh sessions when the client has terminated without disconnecting gracefully
  # eg router reboots all loses 3G signal
  ClientAliveInterval 30
  ClientAliveCountMax 3
  ```

8. Save, close and restart sshd:

```
# systemctl restart sshd
```

9. Confirm ssh works on the new port:

  ```
  ssh -i [your private key] root@[your elastic IP address]:[your custom ssh port, eg 12206]
  ```
  
  or PuTTY equivalent on Windows.
10. Exit

## Create ssh keys for mesh router and add to ssh server
OpenWrt runs `dropbear`, a lightweight implementation of `ssh`. Some additional steps are required to get public key authentication working from the router to the ssh server as keys generated by `ssh-keygen` arent understood by dropbear.

1. ssh onto the router:

  ```
  ssh root@[router IP address]
  ```
  
  or PuTTY equivalent on Windows.
2. Create ssh key pair on the router:
  ```
  # dropbearkey -t rsa -f /etc/dropbear/id_dropbear
  # dropbearkey -y -f .ssh/id_dropbear >> .ssh/id_dropbear.pub
  ```
3. scp the router public key to the ssh server via your client:
  ```
  $ scp root@[router IP address]:/root/.ssh/id_dropbear.pub ./
  $ scp ./id_dropbear.pub root@[your elastic IP address]:/root/.ssh/
  ```
  or use WinSCP equivalent on Windows.
4. On your client, ssh onto the ssh server:
  ```
  # Arch Linux
  ssh -i [your private key] root@[your elastic IP address]:[your custom ssh port]
  # Ubuntu
  ssh -i [your private key] ubuntu@[your elastic IP address]:[your custom ssh port]
  ```
  or PuTTY equivalent on Windows.
5. On the ssh server, add the router public key to authorized keys:
  ```
  cat .ssh/id_dropbear.pub >> .ssh/authorized_keys
  ```
6. On the router, test the ssh connection
  ```
  # Arch Linux
  ssh -i [your private key] root@[your elastic IP address]:[your custom ssh port]
  # Ubuntu
  ssh -i [your private key] ubuntu@[your elastic IP address]:[your custom ssh port]
  ```
  
## Configure the reverse ssh tunnel
  
### Test reverse ssh tunnel
First test that a reverse ssh tunnel from ssh server to router works:
1. On the router whose reverse tunnel entrance will be proxied on the ssh server on port 15001, run:

  ```
  ssh -fNT -R 15001:localhost:22 root@[your elastic IP address]/[your custom ssh port]
  ```

2.  On the ssh server, run:

  ```
  ssh localhost -p 15001
  ```

  You should now have an ssh terminal into the router from the ssh server.
  
## Enable persistent reverse tunnel

1. ssh onto the router.
2. Install autossh
  
  ```
  opkg update
  opkg install autossh
  ```
  
3. Put [this startup script](https://github.com/SEBA-Smart-Services/smartnet/blob/master/batman_mesh_network/util/reversessh.init) in `/etc/init.d/reversessh`.
4. Enable cron: ` # /etc/init.d/cron/enable`
5. Edit crontab with an entry to start the service on a schedule, eg for 5 every minutes:
  
  ```
  # crontab -e
  */5 * * * * /etc/init.d/reversessh start
  ```
  
6. Test by starting cron: ` # /etc/init.d/cron/start`
7. Wait until schedule executes and check service:

  ```
  # ps |grep ssh
   3024 root       652 S    /usr/bin/autossh -M 0    -nNT -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -R
   3025 root       868 S    /usr/bin/ssh -nNT -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -R 15002:localh
  ```

## OPTIONAL: monitor reverse ssh tunnel status
A script can run on the ssh server to monitor the status reverse ssh tunnel connections. 

A working [python 2 script can be found here](https://github.com/SEBA-Smart-Services/smartnet/blob/master/batman_mesh_network/util/reverse_ssh_monitor.py). This script writes the reverse ssh tunnel connections to a logfile in `/var/log/reverse-ssh-monitor`. This script can be put into `/opt` and executed on a schedule using cron. Example crontab entry as follows:

```
*/30 * * * * /usr/bin/python2 /opt/reverse_ssh_monitor.py
```

TODO: enhance script to send emails and/or Pushover notifications if connections drop out.
