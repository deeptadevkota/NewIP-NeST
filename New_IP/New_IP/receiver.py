# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @rohit-mp @bhaskar792 @shashank68

import signal
import time
from scapy.all import *
from New_IP.sender import Sender
from New_IP.newip_hdr import (
    ShippingSpec,
    NewIPOffset,
    Ping,
    LatencyBasedForwarding,
)
from extras.parse_receiver import parse_receiver

ADDR_TYPES = {0: "ipv4", 1: "ipv6", 2: "8bit"}


class Receiver:
    @staticmethod
    def process_pkt(self, pkt, iface):
        self.pkt_count = self.pkt_count + 1

        if pkt[Ether].type == 0x0800:
            # IPv4
            print("legacy IPv4 packet received")
        elif pkt[Ether].type == 0x86DD:
            # IPv6
            print("Legacy IPv6 packet received")
        elif pkt[Ether].type == 0x88B6:
            # NEW IP

            ship_layer = ShippingSpec(pkt[Raw].load)
            pkt_details = (
                f"sa:{ship_layer.src} "
                f"st:{ADDR_TYPES[ship_layer.src_addr_type]} "
                "<--> "
                f"da:{ship_layer.dst} "
                f"dt:{ADDR_TYPES[ship_layer.dst_addr_type]}"
            )
            ship_payload = ship_layer[Raw].load

            if pkt[NewIPOffset].contract_offset != 0:
                # Contract exists

                # Check the type of contract
                if bytes(ship_payload)[:2] == b"\x00\x03":
                    # ping contract
                    ping_contract = Ping(ship_payload)
                    ping_code = ping_contract[Ping].code
                    pkt_details = f"{pkt_details} contract:ping [{ping_code}]"

                    if ping_code == 0:
                        # Ping request packet

                        # Get the sending timestamp
                        snder_ts = ping_contract[Ping].timestamp

                        # Send a response back
                        pong_sender = Sender()
                        pong_sender.make_packet(
                            src_addr_type=ship_layer.dst_addr_type,
                            src_addr=ship_layer.dst,
                            dst_addr_type=ship_layer.src_addr_type,
                            dst_addr=ship_layer.src,
                            content="PONG",
                        )
                        pong_sender.insert_contract(
                            "ping_contract", params=[1, snder_ts]
                        )
                        pong_sender.send_packet(iface=iface)
                    else:
                        # Received a Ping reply
                        rtt = round(
                            time.time_ns() // 1000000 - ping_contract[Ping].timestamp, 4
                        )
                        print(
                            f"PING reply from {ship_layer.src} time={rtt}ms ttl={ping_contract[Ping].hops}"
                        )
                else:
                    # lbf contract
                    lbf_layer = LatencyBasedForwarding(ship_payload)
                    lbf_contract = lbf_layer[LatencyBasedForwarding]
                    lbf_params = (
                        f"{lbf_contract.min_delay}, "
                        f"{lbf_contract.max_delay}, "
                        f"{lbf_contract.experienced_delay}"
                    )
                    pkt_details = f"{pkt_details} contract:lbf [{lbf_params}]"
                    # print(
                    #         f"PING reply from {ship_layer.src} time={rtt}ms ttl={ping_contract[Ping].hops}"
                    #     )

            if self.verbose == 2 or self.verbose >= 4:
                os.system('echo "' + pkt_details + '" >> ' + self.filename)
            if self.verbose >= 3:
                print(pkt_details)

    def __init__(self, node, verbose=1, folder="", timeout =0):
        self.sniff_thread = None
        self.pkt_list = []
        self.pkt_count = 0
        self.verbose = verbose
        conf.route.resync()
        conf.sniff_promisc = 0
        self.node = node
        self.timeout = timeout
        if(self.timeout == 0):
            self.timeout = 5000
        if folder != "":
            self.filename = (
                folder
                + "/receiver_stats_"
                + time.strftime("%d-%m-%Y-%H:%M:%S")
                + ".txt"
            )
        else:
            self.filename = (
                "receiver_stats_" + time.strftime("%d-%m-%Y-%H:%M:%S") + ".txt"
            )


    def exit_gracefully(self, *args):
        # print("************* GRACEFULLY")
        print("[INFO] " + str(self.pkt_count) + " New-IP pkts received at " + self.node.name)


    def start(self, iface):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        if not isinstance(iface, str):
            iface = iface.name
        # print("about to sniff!!!!")
        print("******* timeout is *********** ", self.timeout)
        self.pkt_list = sniff(
            iface=iface,
            filter="((ether proto 0x88b6) or (ip proto 254)) and inbound",
            prn=lambda x: self.process_pkt(self, x, iface),
            timeout=self.timeout,
        )
        # self.sniff_thread.start()
        # print("Started sniffer!!!!")
        if self.verbose >= 1:
            print("[INFO] " + str(len(self.pkt_list)) + " New-IP pkts received at " + self.node.name)
        # if verbose == 2 or verbose >= 4:
        #     parse = parse_receiver(self.filename)
        #     parse.read_receiver_file()
        #     parse.dump_jitter()
        #     parse.plot()

