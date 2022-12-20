# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @kiranmak @bhaskar792 @shashank68

# This program sends New-IP, LBF contract, Legacy IP or Ping contract packet
# from the source to the destination provider by the users
# by default it sends New-IP packet
# mixed flow traffic with multiple sender and receivers can be obtained
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
import random
import string
import time
import os
import multiprocessing
from New_IP.setup import Setup
from New_IP.sender import Sender, LegacyIpSender
from New_IP.newip_hdr import LatencyBasedForwarding, Ping
from datetime import datetime
from lbf_forwarder_args import lbf_forwarder_args

qdisc = "lbf"


class LbfObj:
    def __init__(self, min_delay, max_delay, hops):
        # define main variables you want to store and use
        self.c_min_delay = int(min_delay)
        self.c_max_delay = int(max_delay)
        self.hops = int(hops)
        self.fib_delay = 0

    def get_lbf_params(self):
        return [self.c_min_delay, self.c_max_delay, 0, self.hops]

    def set_lbf_params(self, min_delay, max_delay, hops):
        self.c_min_delay = int(min_delay)
        self.c_max_delay = int(max_delay)
        self.hops = int(hops)


class lbf_forwarder:
    # define start of forwarder. the interval and pkt count.
    def __init__(self, min_delay=50, max_delay=60):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.args = lbf_forwarder_args()
        self.netObj = Setup()
        self.netObj.setup_topology()
        self.srcNode = []
        for src in self.args.src:
            self.srcNode.append(self.netObj.info_dict[src]["node"])
        self.dstNode = []
        for dst in self.args.dst:
            self.dstNode.append(self.netObj.info_dict[dst]["node"])
        recVerbose = True
        if (
            self.args.pcapAll
            or self.args.pcapDst
            or self.args.pcapInterfaceList
            or self.args.pcapNodeList
            or self.args.useTcpReplay
        ):
            self.pcapDirName = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
            try:
                os.remove("./latest")
            except OSError:
                pass
            os.symlink(self.pcapDirName, "./latest")
        if self.args.pcap == "":
            if self.args.useTcpReplay:
                self.netObj.generate_pcap(
                    timeout=self.args.timeout,
                    nodelist=self.srcNode,
                    dir_name=self.pcapDirName,
                )
                recVerbose = False
            else:
                self.gen_pcap()

            self.netObj.start_receiver(
                timeout=self.args.timeout, nodeList=self.dstNode, verbose=recVerbose
            )
            self.start_forwarder()

        if self.args.useTcpReplay:
            self.replay()

    def gen_pcap(self):
        if self.args.pcapAll:
            self.netObj.generate_pcap(
                timeout=self.args.timeout, dir_name=self.pcapDirName
            )
        elif self.args.pcapDst:
            self.netObj.generate_pcap(
                timeout=self.args.timeout,
                nodelist=self.dstNode,
                dir_name=self.pcapDirName,
            )
        elif self.args.pcapInterfaceList:
            self.netObj.generate_pcap(
                timeout=self.args.timeout,
                interfaces=self.args.pcapInterfaceList,
                dir_name=self.pcapDirName,
            )
        elif self.args.pcapNodeList:
            self.netObj.generate_pcap(
                timeout=self.args.timeout,
                nodelist=self.args.pcapNodeList,
                dir_name=self.pcapDirName,
            )

    def pkt_fill(self, index):
        START = "pkt# %d " % (index)
        remaining = self.args.pktSize - len(START)
        chars = string.ascii_uppercase + string.digits
        return START + "".join(random.choice(chars) for _ in range(remaining))

    def create_lbf_pkt(self, sender, srcNode, dstNode, content, nolbf=False):
        src_addr_type = random.choice(self.args.src_addr_type)
        dst_addr_type = random.choice(self.args.dst_addr_type)
        src_addr = self.netObj.info_dict[srcNode.name][src_addr_type]
        dst_addr = self.netObj.info_dict[dstNode.name][dst_addr_type]
        sender.make_packet(
            src_addr_type,
            src_addr,
            dst_addr_type,
            dst_addr,
            content,
        )

        if not nolbf and self.args.lbfList != None:
            hops = self.netObj.info_dict[srcNode.name]["hops"][dstNode.name]
            self.lbfObj = LbfObj(self.min_delay, self.max_delay, hops)

            if self.args.lbfList != []:
                rand_min_index = random.choice(range(0, len(self.args.lbfList), 2))
                min_delay = self.args.lbfList[rand_min_index]
                max_delay = self.args.lbfList[rand_min_index + 1]

                self.lbfObj.set_lbf_params(min_delay, max_delay, hops)

            params = self.lbfObj.get_lbf_params()
            lbf_contract = LatencyBasedForwarding(
                min_delay=params[0],
                max_delay=params[1],
                fib_todelay=params[2],
                fib_tohops=params[3],
            )
            sender.set_contract([lbf_contract])
            # self.sender.insert_contract("latency_based_forwarding", params)

    def create_ping_pkt(self, sender, srcNode, dstNode):
        src_addr_type = random.choice(self.args.src_addr_type)
        dst_addr_type = random.choice(self.args.dst_addr_type)
        src_addr = self.netObj.info_dict[srcNode.name][src_addr_type]
        dst_addr = self.netObj.info_dict[dstNode.name][dst_addr_type]
        sender.make_packet(src_addr_type, src_addr, dst_addr_type, dst_addr, "PING")
        sending_ts = time.time_ns() // 1000000
        ping_contract = Ping(code=0, timestamp=sending_ts)
        sender.set_contract([ping_contract])

    def create_legacyip_pkt(self, sender, srcNode, dstNode, content):
        addr_type = self.args.src_addr_type
        if "8bit" in addr_type:
            addr_type.remove("8bit")
        addr_type = random.choice(addr_type)
        src_addr = self.netObj.info_dict[srcNode.name][addr_type]
        dst_addr = self.netObj.info_dict[dstNode.name][addr_type]
        sender.make_packet(
            src_addr=src_addr,
            dst_addr=dst_addr,
            content=content,
        )

    def sender_process(self, srcNode):
        with srcNode:
            dstNode = self.dstNode
            if srcNode in dstNode:
                dstNode.remove(srcNode)
            if dstNode:
                srcIf = srcNode._interfaces[0].name
                if self.args.useTcpReplay:
                    os.system(f"tc qdisc replace dev {srcIf} root pfifo")

                for index in range(
                    max(int(self.args.pktCount / len(self.args.src)), 1)
                ):
                    rand_dst_node = random.choice(dstNode)
                    packet_type = random.choice(self.args.packet_types)
                    if packet_type == "li":
                        sender = LegacyIpSender()
                    else:
                        sender = Sender()
                    if packet_type == "ping":
                        self.create_ping_pkt(sender, srcNode, rand_dst_node)
                    elif packet_type == "li":
                        self.create_legacyip_pkt(sender, srcNode, rand_dst_node, index)
                    else:
                        payload = self.pkt_fill(index)
                        if packet_type == "nolbf":
                            self.create_lbf_pkt(
                                sender, srcNode, rand_dst_node, payload, nolbf=True
                            )
                        else:
                            self.create_lbf_pkt(sender, srcNode, rand_dst_node, payload)

                    sender.send_packet(iface=srcIf, show_pkt=self.args.showPacket)

    def start_forwarder(self):
        if self.args.ping:
            self.netObj.start_receiver(
                timeout=self.args.timeout, nodeList=self.srcNode, verbose=True
            )

        for srcNode in self.srcNode:
            sender_proc = multiprocessing.Process(
                target=self.sender_process, args=(srcNode,)
            )
            sender_proc.start()

    def tcp_replay_process(self, srcNode, srcIf, replayFile):
        with srcNode:
            if self.args.trTopspeed:
                os.system(
                    f"sudo timeout {self.args.timeout} tcpreplay --loop={self.args.trLoop} --stats={self.args.trStats} --topspeed -i {srcIf} {replayFile} "
                )
            elif self.args.trMbps:
                os.system(
                    f"sudo timeout {self.args.timeout} tcpreplay --loop={self.args.trLoop} --stats={self.args.trStats} --Mbps={self.args.trMbps} -i {srcIf} {replayFile} "
                )
            else:
                os.system(
                    f"sudo timeout {self.args.timeout} tcpreplay --loop={self.args.trLoop} --stats={self.args.trStats} --pps={self.args.trPps} -i {srcIf} {replayFile} "
                )

    def replay(self):
        self.netObj.start_receiver(timeout=self.args.timeout, nodeList=self.dstNode)
        if self.args.pcap == "":
            print("waiting for receiver processes to end...")
            time.sleep(self.args.timeout)
        for srcNode in self.srcNode:
            srcIf = srcNode._interfaces[0].name
            if self.args.pcap == "":
                os.system(
                    f"cp {self.pcapDirName}/{srcIf}.pcap {self.pcapDirName}/replay_{srcIf}.pcap"
                )
                with srcNode:
                    os.system(f"tc qdisc replace dev {srcIf} root " + qdisc)
                replayFile = f"{self.pcapDirName}/replay_{srcIf}.pcap"
            else:
                replayFile = self.args.pcap
            tcp_replay_proc = multiprocessing.Process(
                target=self.tcp_replay_process,
                args=(
                    srcNode,
                    srcIf,
                    replayFile,
                ),
            )
            tcp_replay_proc.start()

            self.gen_pcap()


lbf_forwarder_obj = lbf_forwarder()
