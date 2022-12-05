# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @deeptadevkota

# This program sends legacy IP packet from the source
# to the destination provided by the user
# by default the the src is h1 and dst is h2
# the default packet count is 1
# the default source and destination type is ipv4
# the pcap capture can be enabled as per the user preference


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

import argparse
import os
import random
from New_IP.setup import Setup
from New_IP.sender import LegacyIpSender
from datetime import datetime


class Legacy_ip_application:
    def __init__(self):
        self.set_args()
        self.parse_args()
        self.netObj = Setup()
        self.netObj.setup_topology()

        self.srcNode = self.netObj.info_dict[self.src]["node"]
        self.dstNode = self.netObj.info_dict[self.dst]["node"]
        self.srcIf = self.srcNode._interfaces[0].name

        recVerbose = True

        if self.pcapAll or self.pcapDst or self.pcapInterfaceList or self.pcapNodeList:
            self.pcapDirName = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
            try:
                os.remove("./latest")
            except OSError:
                pass
            os.symlink(self.pcapDirName, "./latest")

        self.gen_pcap()

        self.netObj.start_receiver(
            timeout=self.timeout, nodeList=[self.dstNode], verbose=recVerbose
        )
        self.start_forwarder()

    def gen_pcap(self):
        if self.pcapAll:
            self.netObj.generate_pcap(timeout=self.timeout, dir_name=self.pcapDirName)
        elif self.pcapDst:
            self.netObj.generate_pcap(
                timeout=self.timeout,
                nodelist=[self.dstNode],
                dir_name=self.pcapDirName,
            )
        elif self.pcapInterfaceList:
            self.netObj.generate_pcap(
                timeout=self.timeout,
                interfaces=self.pcapInterfaceList,
                dir_name=self.pcapDirName,
            )
        elif self.pcapNodeList:
            self.netObj.generate_pcap(
                timeout=self.timeout,
                nodelist=self.pcapNodeList,
                dir_name=self.pcapDirName,
            )

    def set_args(self):
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument(
            "--src-type",
            "-st",
            choices={"8bit", "ipv4", "ipv6"},
            default="ipv4",
            help="set source address type",
        )
        self.parser.add_argument(
            "--src",
            "-sa",
            choices={"h1", "h2", "h3"},
            default="h1",
            help="set source host",
        )
        self.parser.add_argument(
            "--dst-type",
            "-dt",
            choices={"8bit", "ipv4", "ipv6"},
            default="ipv4",
            help="set dst address type",
        )
        self.parser.add_argument(
            "--dst",
            "-da",
            choices={"h1", "h2", "h3"},
            default="h2",
            help="set destination host",
        )
        self.parser.add_argument(
            "--timeout",
            "-t",
            type=int,
            default=10,
            help="timeout for receiver and pcap capture",
        )
        self.parser.add_argument(
            "--pcap-all",
            "-pa",
            action="store_true",
            default=False,
            help="Capture pcap for all nodes",
        )
        self.parser.add_argument(
            "--pcap-dst",
            "-pd",
            action="store_true",
            default=False,
            help="Capture pcap for dst node",
        )
        self.parser.add_argument(
            "--pcap-interface-list",
            "-pil",
            action="append",
            default=None,
            help="Capture packets on this list of interface",
        )
        self.parser.add_argument(
            "--pcap-node-list",
            "-pnl",
            action="append",
            default=None,
            help="Capture packets on this list of nodes",
        )
        self.parser.add_argument(
            "--pkt-count", "-c", type=int, default=1, help="number of pkts to send"
        )
        self.parser.add_argument(
            "--show-packet",
            "-sp",
            action="store_true",
            default=False,
            help="Show Packet",
        )

    def parse_args(self):
        # Read arguments from the command line
        args = self.parser.parse_args()

        self.src_addr_type = args.src_type
        self.dst_addr_type = args.dst_type
        self.src = args.src
        self.dst = args.dst
        self.pktCount = args.pkt_count
        self.timeout = args.timeout
        self.showPacket = args.show_packet

        self.pcapAll = args.pcap_all
        self.pcapDst = args.pcap_dst
        self.pcapNodeList = args.pcap_node_list
        self.pcapInterfaceList = args.pcap_interface_list

    def create_legacyip_pkt(self, content):
        self.sender.make_packet(
            self.src_addr,
            self.dst_addr,
            content,
        )

    def start_forwarder(self):
        self.src_addr = self.netObj.info_dict[self.src][self.src_addr_type]
        self.dst_addr = self.netObj.info_dict[self.dst][self.dst_addr_type]

        with self.srcNode:
            self.sender = LegacyIpSender()
            for index in range(self.pktCount):
                self.create_legacyip_pkt(index)
                self.sender.send_packet(iface=self.srcIf, show_pkt=self.showPacket)


legacy_ip_application_obj = Legacy_ip_application()
