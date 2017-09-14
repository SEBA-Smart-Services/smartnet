# reverse_ssh_monitor.py
#
# get entries in netstat table related to reverse ssh tunnels and record in log
# execute this using crontab, eg:
#   */30 * * * * /usr/bin/python2 /opt/reverse_ssh_monitor.py
#
# example netstat output:
#        Active Internet connections (servers and established)
#        Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
#        tcp        0      0 127.0.0.1:15001         0.0.0.0:*               LISTEN      2248/sshd: root
#        tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      417/sshd
#        tcp        0      0 0.0.0.0:5355            0.0.0.0:*               LISTEN      299/systemd-resolve
#        tcp        0      0 172.31.8.0:5226         49.197.81.75:30256      ESTABLISHED 2248/sshd: root
#        tcp6       0      0 ::1:15001               :::*                    LISTEN      2248/sshd: root
#        tcp6       0      0 :::22                   :::*                    LISTEN      417/sshd
#        tcp6       0      0 :::5355                 :::*                    LISTEN      299/systemd-resolve
#        tcp6       0    204 172.31.8.0:22           144.140.230.125:56887   ESTABLISHED 1/systemd
#
# example log entry:
# 2017-09-14 13:15:01,346 - INFO:
# Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
# tcp        0      0 127.0.0.1:15001          0.0.0.0:*               LISTEN      2817/sshd: root
# tcp6       0      0 ::1:15001                :::*                    LISTEN      2817/sshd: root
#

import logging
from logging.handlers import RotatingFileHandler
from subprocess import check_output

LOG_FILE = '/var/log/reverse-ssh-monitor/log'
LOG_MAX_BYTES = 1024*1024*2
LOG_BACKUP_COUNT = 10

TUNNEL_PORT_RANGE = range(15001, 15011)
TUNNEL_PROTOCOLS = ['tcp', 'tcp6']

# configure log
log_format='%(asctime)s - %(levelname)s: %(message)s'
logger = logging.getLogger('log')
log_handler = RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT)
log_handler.setLevel(logging.INFO)
log_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

# execute netstat command
netstat_raw = check_output(['netstat', '-vatnp'])

# skip header lines
skip_lines = 2
netstat = [line.split() for line in netstat_raw.splitlines()][skip_lines:]

# NOT USED
def make_log_entry(conn):
    entry = '\n'.join([
        'there he fucking is!',
        'local address: ' + conn[3],
        'foreign address: ' + conn[4],
        'state: ' + conn[5],
        'PID/program name: ' + conn[6]
    ])
    return entry

# get index of relevant entries in netstat table
lines_of_interest = []
for n, conn in enumerate(netstat):
    # local port is 4th col after the ':'
    port = conn[3].split(':')[-1]
    protocol = conn[0]
    # only care about IPv4 tcp connections at this stage
    if protocol in TUNNEL_PROTOCOLS:
        # check if local port in TUNNEL_PORT_RANGE
        if port in map(str, TUNNEL_PORT_RANGE):
            entry = make_log_entry(conn)
