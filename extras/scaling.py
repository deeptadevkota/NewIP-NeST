# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @rohit-mp @bhaskar792

from nest.experiment import *
from nest.topology import *
from nest.routing.routing_helper import RoutingHelper
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper
import nest.config as config

from scapy.all import *

import multiprocessing
import os

# from router import router
from New_IP.receiver import Receiver
from New_IP.sender import Sender

qdisc = "lbf"

config.set_value("assign_random_names", False)
# config.set_value('delete_namespaces_on_termination', False)
config.set_value("routing_logs", True)

# Checking if the right arguments are input
if len(sys.argv) != 3:
    print("usage: python3 scaling.py <number-of-ipv4-senders> <number-of-ipv6-senders>")
    sys.exit(1)

# Assigning number of nodes on either sides of the dumbbell according to input
num_of_ipv4_senders = int(sys.argv[1])
num_of_ipv6_senders = int(sys.argv[2])

# Verify no errors in xdp programs
if os.system("make -C xdp/newip_router/") != 0:
    exit()

# Verify no errors in qdisc
if os.system("cd lbf; ./install-module") != 0:  # TODO doesn't seem to work
    exit()

# Lists to store all sender nodes
ipv4_senders = []
ipv6_senders = []

# Creating all sender nodes
for i in range(num_of_ipv4_senders):
    ipv4_senders.append(Node("v4-" + str(i)))

for i in range(num_of_ipv6_senders):
    ipv6_senders.append(Node("v6-" + str(i)))

# h = host
h1 = Node("h1")
h2 = Node("h2")
h3 = Node("h3")

# r = router
r1 = Node("r1")
r2 = Node("r2")
r3 = Node("r3")

r1.enable_ip_forwarding()
r2.enable_ip_forwarding()
r3.enable_ip_forwarding()

# Define networks
ipv4_sender_network = Network("10.0.0.0/24")
ipv6_sender_network = Network("10::/122")

# Lists to store all sender connections
ipv4_sender_connections = []
ipv6_sender_connections = []

# Connecting senders to router r1
for i in range(num_of_ipv4_senders):
    ipv4_sender_connections.append(
        connect(ipv4_senders[i], r1, network=ipv4_sender_network)
    )

for i in range(num_of_ipv6_senders):
    ipv6_sender_connections.append(
        connect(ipv6_senders[i], r1, network=ipv6_sender_network)
    )

# Assign addresses to each interface present in network
AddressHelper.assign_addresses()

# Connect and assign address to rest of the nodes
(r1_h1, h1_r1) = connect(r1, h1)
(r2_h2, h2_r2) = connect(r2, h2)
(r3_h3, h3_r3) = connect(r3, h3)
(r1_r2, r2_r1) = connect(r1, r2)
(r1_r3, r3_r1) = connect(r1, r3)

h1_r1.set_address("10.0.1.2/24")
r1_h1.set_address("10.0.1.1/24")
h2_r2.set_address("10.0.2.2/24")
r2_h2.set_address("10.0.2.1/24")
h3_r3.set_address("10::3:2/122")
r3_h3.set_address("10::3:1/122")

r1_r2.set_address("10.0.4.1/24")
r2_r1.set_address("10.0.4.2/24")
r1_r3.set_address("10.0.5.1/24")
r3_r1.set_address("10.0.5.2/24")
RoutingHelper(protocol="rip").populate_routing_tables()
r1_r2.set_address("10::4:1/122")
r2_r1.set_address("10::4:2/122")
r1_r3.set_address("10::5:1/122")
r3_r1.set_address("10::5:2/122")
RoutingHelper(protocol="rip").populate_routing_tables()
# Populating routing tables twice to populate both v4 and v6 tables

# Create 'routing table' for 8bit address
static_redirect_8b = {
    "r1": {
        1: r1_h1.name,
        2: r1_r2.name,
        3: r1_r3.name,
    },
    "r2": {
        1: r2_r1.name,
        2: r2_h2.name,
        3: r2_r1.name,
    },
    "r3": {
        1: r3_r1.name,
        2: r3_r1.name,
        3: r3_h3.name,
    },
    "h1": {
        2: h1_r1.name,
        3: h1_r1.name,
    },
    "h2": {
        1: h2_r2.name,
        2: h2_r2.name,
    },
    "h3": {
        1: h3_r3.name,
        2: h3_r3.name,
    },
}


def receiver_proc(node, iface):
    receiver_obj = Receiver(node)
    receiver_obj.start(iface=iface)


def sender_proc(node, iface, src_addr_type, delay=100):
    sender_obj = Sender()
    # to IPv4
    sender_obj.make_packet(
        src_addr_type=src_addr_type,
        src_addr=iface.address,
        dst_addr_type="ipv4",
        dst_addr=h2.get_interface(r2).address,
        content=src_addr_type + " to ipv4, to h2",
    )
    sender_obj.insert_contract(contract_type="max_delay_forwarding", params=[delay])
    sender_obj.send_packet(iface=iface, show_pkt=True)

    # to IPv6
    sender_obj.make_packet(
        src_addr_type=src_addr_type,
        src_addr=iface.address,
        dst_addr_type="ipv6",
        dst_addr=h3.get_interface(r3).address,
        content=src_addr_type + " to ipv6, to h3",
    )
    sender_obj.insert_contract(contract_type="max_delay_forwarding", params=[delay])
    sender_obj.send_packet(iface=iface)


def setup_router(node, interfaces):
    route = ""
    for key, value in static_redirect_8b[node.name].items():
        # TODO verify if extra '-' at end is ok
        route = route + str(key) + "_" + value + "-"
    with node:
        for interface in interfaces:
            os.system(
                "./New_IP/xdp/newip_router/xdp_loader --progsec xdp_router --filename ./New_IP/xdp/newip_router/xdp_prog_kern.o --dev "
                + interface.name
            )
            os.system(
                "sudo ./New_IP/xdp/newip_router/xdp_prog_user --filename "
                + route
                + " -d "
                + interface.name
            )
            os.system("tc qdisc add dev " + interface.name + " ingress")
            os.system(
                "tc filter add dev "
                + interface.name
                + " ingress bpf da obj ./New_IP/xdp/newip_router/tc_prog_kern.o sec tc_router"
            )
            os.system("tc qdisc replace dev " + interface.name + " root " + qdisc)


def setup_host(node, interfaces):
    with node:
        for interface in interfaces:
            # os.system(
            #     './xdp/newip_router/xdp_loader --progsec xdp_pass --filename ./xdp/newip_router/xdp_prog_kern.o --dev ' + interface.name)
            os.system("tc qdisc replace dev " + interface.name + " root " + qdisc)


# Setup xdp programs for bidirectional flow
# TODO discuss on showing or removing the output from xdp_loader and tc

for sender in ipv4_senders:
    setup_host(sender, [sender.get_interface(r1)])
for sender in ipv6_senders:
    setup_host(sender, [sender.get_interface(r1)])

setup_host(h2, [h2.get_interface(r2)])
setup_host(h3, [h3.get_interface(r3)])

setup_router(r1, r1.interfaces)
setup_router(r2, r2.interfaces)
setup_router(r3, r3.interfaces)

with h2:
    receiver_process = multiprocessing.Process(
        target=receiver_proc,
        args=(
            h2,
            h2.get_interface(r2),
        ),
    )
    receiver_process.start()
with h3:
    receiver_process = multiprocessing.Process(
        target=receiver_proc,
        args=(
            h3,
            h3.get_interface(r3),
        ),
    )
    receiver_process.start()

# Ensure routers and receivers have started
time.sleep(1)

ipv4_sender_processes = []
ipv6_sender_processes = []
for sender in ipv4_senders:
    with sender:
        ipv4_sender_processes.append(
            multiprocessing.Process(
                target=sender_proc, args=(sender, sender.get_interface(r1), "ipv4")
            )
        )
        ipv4_sender_processes[len(ipv4_sender_processes)].start()
for sender in ipv6_senders:
    with sender:
        ipv6_sender_processes.append(
            multiprocessing.Process(
                target=sender_proc, args=(sender, sender.get_interface(r1), "ipv4")
            )
        )
        ipv6_sender_processes[len(ipv6_sender_processes)].start()

for process in ipv4_sender_processes:
    process.join()
for process in ipv6_sender_processes:
    process.join()
receiver_process.join()
# XDP programs end when namespaces are deleted
