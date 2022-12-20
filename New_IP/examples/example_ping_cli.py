# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @deeptadevkota

# This program sends ping contract packet from the source
# to the destination provided by the user
# by default the the src is h1 and dst is h2
# the default packet count is 1
# the default source and destination type is ipv4


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
import time
from New_IP.setup import Setup
from New_IP.sender import Sender
from New_IP.newip_hdr import Ping


class ping_application:
    def __init__(self):
        self.set_args()
        self.parse_args()
        self.netObj = Setup()
        self.netObj.setup_topology()

        self.srcNode = self.netObj.info_dict[self.src]["node"]
        self.dstNode = self.netObj.info_dict[self.dst]["node"]
        self.srcIf = self.srcNode._interfaces[0].name
        recVerbose = True

        self.netObj.start_receiver(
            timeout=self.timeout, nodeList=[self.dstNode], verbose=recVerbose
        )
        self.start_forwarder()

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
            "--pkt-count", "-c", type=int, default=1, help="number of pkts to send"
        )
        self.parser.add_argument(
            "--timeout",
            "-t",
            type=int,
            default=10,
            help="timeout for receiver and pcap capture",
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

    def create_ping_pkt(self):
        self.sender.make_packet(
            self.src_addr_type, self.src_addr, self.dst_addr_type, self.dst_addr, "PING"
        )
        sending_ts = time.time_ns() // 1000000
        ping_contract = Ping(code=0, timestamp=sending_ts)
        self.sender.set_contract([ping_contract])

    def start_forwarder(self):

        self.src_addr = self.netObj.info_dict[self.src][self.src_addr_type]
        self.dst_addr = self.netObj.info_dict[self.dst][self.dst_addr_type]

        self.netObj.start_receiver(
            timeout=self.timeout, nodeList=[self.srcNode], verbose=True
        )

        with self.srcNode:
            self.sender = Sender()
            for index in range(self.pktCount):
                self.create_ping_pkt()
                self.sender.send_packet(iface=self.srcIf, show_pkt=self.showPacket)


ping_application_obj = ping_application()
