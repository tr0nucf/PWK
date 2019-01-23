#!./venv/bin/python3
#!--*--coding:utf-8--*--
__author__ = 'Cazin Christophe'

# Declaration part ####################################################################
import socket
import argparse, textwrap
#import os
import threading
import queue
import sys
import time

NUMBER_OF_THREADS = 20
timeout_threads = 0.5
portlist = range(1024)
commom_ports = {
    21:  "ftp",
    22:  "ssh",
    23:  "telnet",
    25:  "smtp",
    53:  "dns",
    80:  "http",
    110: "pop3",
    139: "netbios",
    443: "https",
    445: "microsoft-ds",
}# host = sys.argv[1]
port_queue = queue.Queue()  # Create a Queue object

# Function part ####################################################################
# Treate / get / parse arguments
def get_args():
    host_l=""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = textwrap.dedent('''\
        Script who scan port for a host or a list of hosts and more ...
        Using for PWK OSCP exam
        '''))
    # Add either -net or -target but one is required
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-target", "-t", metavar="host", type=str, nargs='+',
                       help="one or more target hostnames or IP adresses to scan. e.g : -t 10.0.0.2,localhost ")
    group.add_argument("-net", "-n", metavar="net", type=str, nargs='+',
                       help="network e.g: -net 10.11.0.0/24 ")
    parser.add_argument('-port', '-p', metavar='p', required=True, type=str, nargs='+',
                        help="list of port and/or range ( -p 1,80,100,105-120)")
    # parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    #host_list = args.target[0].split(",")
    if args.net:
        return args.net[0].split(","), args.port[0].split(",")
    elif args.target:
        return args.target[0].split(","), args.port[0].split(",")


# Open socket for host,port association . Return boolean
def is_port_open(host, port):
    try:
        print("Host/port {}".format((host, port)))
        sock = socket.socket()
        sock.settimeout(timeout_threads)
        sock.connect((host, int(port)))
    except socket.error:
        return False  # port not open
    return True  # port open


# Launch function is_port_open in get port number in the queue ########################
# what I want to launch in my thread
def scanner_worker_thread():
    while True:
        host, port = port_queue.get()  # Get the next (host,port) in the queue

        if is_port_open(host, port):
            if int(port) in commom_ports:
                print("{}({}) is OPEN!".format(port, commom_ports[int(port)]))
            else:
                print("{} is OPEN!".format(port))
        port_queue.task_done()  # After a get in the queue to validate and consume


# Main ###############################################################################
start_time = time.time()

# Get arguments in each list
host_list,port_list = get_args()


# Create thread for each is_port_open
for _ in range(NUMBER_OF_THREADS):
    # Creation of thread can be done with args or kwargs
    t = threading.Thread(target=scanner_worker_thread)
    t.daemon = True
    t.start()

for h in host_list:
    for p in port_list:
        port_queue.put((h, p))  # Fill the queue with tuple (host,port)

port_queue.join()  # Waiting for all threads are terminated. Timeout in second
end_time = time.time()
print("Done. Scanning took {:5.2f} sec".format(end_time - start_time))
