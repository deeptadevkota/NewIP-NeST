# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @rohit-mp @bhaskar792 @shashank68

import signal
from time import sleep
from nest.experiment import *
from nest.topology import *
from nest.routing.routing_helper import RoutingHelper
import nest.config as config

from scapy.all import *

import multiprocessing
import os
import subprocess

from New_IP.receiver import Receiver
from New_IP.tc_stats import tc_stats

# TOPOLOGY
#
#               r2 ---- h2
#              /
#             /
#   h1 ---- r1
#             \
#              \
#               r3 ---- h3
#
####

qdisc = "lbf"


class NewIP:
    def __init__(self) -> None:
        pass

    non_lbf_flows = []
    topo = None

    def create_topology(self):
        topo = Setup()
        topo.setup_topology()
        self.topo = topo

    def add_non_lbf_flows(self, non_lbf_flow):
        self.non_lbf_flows.append(copy.deepcopy(non_lbf_flow))


def tcpdump_proc(interface, timeout, dirName):
    os.system(
        f"timeout {timeout} tcpdump -i "
        + interface.name
        + f" -w {dirName}/"
        + interface.name
        + ".pcap"
        + " ether proto 0x88b6"
        + f" >>  {dirName}/tcpdump_logs.txt 2>&1"
    )


def tc_stats_proc(node, interface, timeout, folder):
    tc_s = tc_stats(node, interface, timeout, folder)


def receiver_proc(node, iface, verbose=True, folder=""):
    # print("HI HELLO I IN RECIEVER PROC****")

    receiver_obj = Receiver(node, verbose, folder)
    receiver_obj.start(iface=iface)

   


def setup_host(node, interfaces):
    with node:
        for interface in interfaces:
            os.system(
                "../New_IP/xdp/newip_router/xdp_loader  --quiet --progsec xdp_pass --filename ../New_IP/xdp/newip_router/xdp_prog_kern.o --dev "
                + interface.name
            )
            os.system("tc qdisc replace dev " + interface.name + " root " + qdisc)


# Create 'routing table' for 8bit address
static_redirect_8b = {
    "r1": {
        1: "r1_h1",
        2: "r1_r2",
        3: "r1_r3",
    },
    "r2": {
        1: "r2_r1",
        2: "r2_h2",
        3: "r2_r1",
    },
    "r3": {
        1: "r3_r1",
        2: "r3_r1",
        3: "r3_h3",
    },
    "h1": {
        2: "h1_r1",
        3: "h1_r1",
    },
    "h2": {
        1: "h2_r2",
        2: "h2_r2",
    },
    "h3": {
        1: "h3_r3",
        2: "h3_r3",
    },
}


def setup_router(node, interfaces, bottleneck_queue_len):
    route = ""
    for key, value in static_redirect_8b[node.name].items():
        route = route + str(key) + "_" + value + "-"
    with node:
        for interface in interfaces:
            os.system(
                "../New_IP/xdp/newip_router/xdp_loader --quiet --progsec xdp_router --filename ../New_IP/xdp/newip_router/xdp_prog_kern.o --dev "
                + interface.name
            )
            os.system(
                "sudo ../New_IP/xdp/newip_router/xdp_prog_user --quiet --filename "
                + route
                + " -d "
                + interface.name
            )
            os.system("tc qdisc add dev " + interface.name + " ingress")
            os.system(
                "tc filter add dev "
                + interface.name
                + " ingress bpf da obj ../New_IP/xdp/newip_router/tc_prog_kern.o sec tc_router"
            )
            os.system(
                f"tc qdisc replace dev "
                + interface.name
                + " root "
                + qdisc
                + " limit "
                + str(bottleneck_queue_len)
            )


def check_and_set_routing_suite(routing):
    rtg_path = os.path.join("/run", routing)
    exists = os.path.exists(rtg_path)
    if exists:
        print("[INFO] : Routing suite is set with", routing)
        return

    # this can be a silent error. next cmd will also fail
    os.system('mkdir "' + rtg_path + '"')

    if os.system("chown  %s %s" % (routing, rtg_path)) != 0:
        print("Routing suite NOT ready ", routing)
        exit(-1)

    print("INFO: Routing suite is set with ", routing)


import logging

logger = logging.getLogger(__name__)


class Setup:
    def __init__(self, resultsFolder=""):
        base_results_folder = "../test_results"
        if not os.path.isdir(base_results_folder):
            os.mkdir(base_results_folder)
        if resultsFolder != "":
            self.folder = base_results_folder + "/" + resultsFolder
            if not os.path.isdir(self.folder):
                os.mkdir(self.folder)
        else:
            self.folder = base_results_folder

    def start_receiver(self, timeout=5, verbose=True, nodeList=[]):
        if not nodeList:
            nodeList = self.hostNodes
        receiver_processes = []
        for node in nodeList:
            for interface in node._interfaces:
                with node:
                    # logging.error("*********** Reciever Procs Started *********")
                    # print("*********** Reciever Procs Started *********")
                    try:
                        receiver_process = multiprocessing.Process(
                            target=receiver_proc,
                            args=(
                                node,
                                interface,
                                timeout,
                                verbose,
                                self.folder,
                            ),
                        )
                    except:
                        print("receiver process error")
                    receiver_process.start()
                    receiver_processes.append(receiver_process)
        # print("*********** Reciever Procs *********")
        # print(receiver_processes)
        return receiver_processes

        # Ensure routers and receivers have started
        # time.sleep(1)

    def generate_pcap(self, interfaces=[], timeout=5, nodelist=[], dir_name="pcap"):
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, dir_name)
        if os.path.exists(final_directory) == False:
            os.makedirs(final_directory, mode=0o777)
        if interfaces:
            nodelist = []
        nodes = self.nodes
        if nodelist:
            nodes = nodelist
        for node in nodes:
            with node:
                for interface in node._interfaces:
                    if (interface.name in interfaces) or not interfaces:
                        tcpdump_process = multiprocessing.Process(
                            target=tcpdump_proc, args=(interface, timeout, dir_name)
                        )
                        tcpdump_process.start()

    def get_tc_stats(self, interfaces=[], timeout=5, nodelist=[]):
        if interfaces:
            nodelist = []
        nodes = self.nodes
        if nodelist:
            nodes = nodelist
        for node in nodes:
            with node:
                for interface in node._interfaces:
                    if (interface.name in interfaces) or not interfaces:
                        print(f"generating tc stats for {interface}")
                        tc_stats_process = multiprocessing.Process(
                            target=tc_stats_proc,
                            args=(node.name, interface.name, timeout, self.folder),
                        )
                        tc_stats_process.start()

    def setup_topology(self, routing="frr", buildLbf=False, bottleneck_queue_len=1000):
        check_and_set_routing_suite(routing)
        config.set_value("assign_random_names", False)
        config.set_value("routing_logs", True)
        # config.set_value('delete_namespaces_on_termination', False)
        # config.set_value("routing_logs", True)
        if routing == "quagga" or routing == "frr":
            config.set_value("routing_suite", routing)
        else:
            print("routing suite not supported")
            exit()

        # Verify no errors in xdp programs
        if os.system("make -C ../New_IP/xdp/newip_router/") != 0:
            exit()

        # Verify no errors in qdisc
        if (
            buildLbf
            or subprocess.Popen(
                'lsmod | grep "sch_lbf"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).communicate()[0]
            == b""
        ):
            if os.system("cd ../New_IP/lbf; ./install-module") != 0:
                exit()
            if os.system("cd ../New_IP/lbf; ./install-tc-support") != 0:
                exit()
        # Create nodes

        # h = host
        self.h1 = Node("h1")
        self.h2 = Node("h2")
        self.h3 = Node("h3")
        # r = router
        self.r1 = Router("r1")
        self.r2 = Router("r2")
        self.r3 = Router("r3")
        self.nodes = [self.h1, self.h2, self.h3, self.r1, self.r2, self.r3]
        self.hostNodes = [self.h1, self.h2, self.h3]
        self.routerNodes = [self.r1, self.r2, self.r3]

        # Create interfaces
        (self.r1_h1, self.h1_r1) = connect(
            self.r1, self.h1, interface1_name="r1_h1", interface2_name="h1_r1"
        )
        (self.r2_h2, self.h2_r2) = connect(
            self.r2, self.h2, interface1_name="r2_h2", interface2_name="h2_r2"
        )
        (self.r3_h3, self.h3_r3) = connect(
            self.r3, self.h3, interface1_name="r3_h3", interface2_name="h3_r3"
        )
        (self.r1_r2, self.r2_r1) = connect(
            self.r1, self.r2, interface1_name="r1_r2", interface2_name="r2_r1"
        )
        (self.r1_r3, self.r3_r1) = connect(
            self.r1, self.r3, interface1_name="r1_r3", interface2_name="r3_r1"
        )

        # Set IPv4 Addresses
        self.h1_r1.set_address("10.0.1.2/24")
        self.r1_h1.set_address("10.0.1.1/24")
        self.h2_r2.set_address("10.0.2.2/24")
        self.r2_h2.set_address("10.0.2.1/24")
        self.h3_r3.set_address("10.0.3.2/24")
        self.r3_h3.set_address("10.0.3.1/24")
        self.r1_r2.set_address("10.0.4.1/24")
        self.r2_r1.set_address("10.0.4.2/24")
        self.r1_r3.set_address("10.0.5.1/24")
        self.r3_r1.set_address("10.0.5.2/24")

        # Set IPv6 Addresses
        self.h1_r1.add_address("10::1:2/122")
        self.r1_h1.add_address("10::1:1/122")
        self.h2_r2.add_address("10::2:2/122")
        self.r2_h2.add_address("10::2:1/122")
        self.h3_r3.add_address("10::3:2/122")
        self.r3_h3.add_address("10::3:1/122")
        self.r1_r2.add_address("10::4:1/122")
        self.r2_r1.add_address("10::4:2/122")
        self.r1_r3.add_address("10::5:1/122")
        self.r3_r1.add_address("10::5:2/122")

        print("ipv4")
        RoutingHelper(protocol="rip").populate_routing_tables()

        print("ipv6")
        RoutingHelper(protocol="rip", ipv6_routing=True).populate_routing_tables()
        # sleep(6000)

        # sleep(6000)

        setup_host(self.h1, [self.h1_r1])
        setup_host(self.h2, [self.h2_r2])
        setup_host(self.h3, [self.h3_r3])
        setup_router(
            self.r1, [self.r1_h1, self.r1_r2, self.r1_r3], bottleneck_queue_len
        )
        setup_router(self.r2, [self.r2_h2, self.r2_r1], bottleneck_queue_len)
        setup_router(self.r3, [self.r3_h3, self.r3_r1], bottleneck_queue_len)

        # TODO automate building this dict
        self.info_dict = {
            "h1": {
                "ipv4": "10.0.1.2",
                "ipv6": "10::1:2",
                "8bit": 0b01,
                "hops": {"h1": 0, "h2": 3, "h3": 3},
                "node": self.h1,
            },
            "h2": {
                "ipv4": "10.0.2.2",
                "ipv6": "10::2:2",
                "8bit": 0b10,
                "hops": {"h1": 3, "h2": 0, "h3": 4},
                "node": self.h2,
            },
            "h3": {
                "ipv4": "10.0.3.2",
                "ipv6": "10::3:2",
                "8bit": 0b11,
                "hops": {"h1": 3, "h2": 4, "h3": 0},
                "node": self.h3,
            },
        }

    def show_stats(self):
        with self.h1:
            print("--h1--")
            os.system("tc -s qdisc show")
        with self.h2:
            print("--h2--")
            os.system("tc -s qdisc show")
        with self.h3:
            print("--h3--")
            os.system("tc -s qdisc show")
        with self.r1:
            print("--r1_r2--")
            os.system("tc -s qdisc show dev r1_r2")
            print("--r1_r3--")
            os.system("tc -s qdisc show dev r1_r3")
        with self.r2:
            print("--r2_h2--")
            os.system("tc -s qdisc show dev r2_h2")
        with self.r3:
            print("--r3_h3--")
            os.system("tc -s qdisc show dev r3_h3")
