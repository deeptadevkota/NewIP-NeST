# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @rohit-mp @bhaskar792 @shashank68

from scapy.all import *


class NewIPOffset(Packet):
    name = "New IP Offset"
    fields_desc = [
        ByteField("shipping_offset", 3),
        ByteField("contract_offset", 0),
        ByteField("payload_offset", 0),
    ]

    def mysummary(self):
        return self.sprintf("NewIP %NewIP.type%")


class ShippingSpec(Packet):
    name = "New IP Shipping Spec"
    sh_addr_type = {0: "ipv4", 1: "ipv6", 2: "8bit"}
    sh_addr_cast = {
        0: "unicast",
        1: "coordcast",
        2: "multicast",
        3: "broadcast",
        4: "groupcast",
    }
    contract_type = {0: "payload", 1: "mdf_contract", 2: "lbf_contract"}
    fields_desc = [
        # Shipping spec
        ByteEnumField("src_addr_type", 0, sh_addr_type),  # Source Address Type
        # Destination Address Type
        ByteEnumField("dst_addr_type", 0, sh_addr_type),
        ByteEnumField("addr_cast", 0, sh_addr_cast),  # Address Cast
        MultipleTypeField(  # Source Address
            [
                # IPv4
                (IPField("src", "127.0.0.1"), lambda pkt: pkt.src_addr_type == 0),
                # IPv6
                (IP6Field("src", "::1"), lambda pkt: pkt.src_addr_type == 1),
                # 8bit
                (ByteField("src", "0"), lambda pkt: pkt.src_addr_type == 2),
            ],
            IPField("src", "127.0.0.1"),
        ),
        MultipleTypeField(  # Destination Address
            [
                # IPv4
                (IPField("dst", "127.0.0.1"), lambda pkt: pkt.dst_addr_type == 0),
                # IPv6
                (IP6Field("dst", "::1"), lambda pkt: pkt.dst_addr_type == 1),
                # 8bit
                (ByteField("dst", "0"), lambda pkt: pkt.dst_addr_type == 2),
            ],
            IPField("dst", "127.0.0.1"),
        ),
        # Contract spec
    ]

    def mysummary(self):
        return self.sprintf("NewIP %NewIP.type%")


class MaxDelayForwarding(Packet):
    name = "Max Delay Forwarding Contract"
    fields_desc = [
        ShortField("contract_type", 1),
        ShortField("max_allowed_delay", 500),
        ShortField("delay_exp", 0),
    ]


class LatencyBasedForwarding(Packet):
    name = "Latency Based Forwarding"
    fields_desc = [
        ShortField("contract_type", 2),
        ShortField("min_delay", 0),
        ShortField("max_delay", 0),
        ShortField("experienced_delay", 0),
        ShortField("fib_todelay", 0),
        ShortField("fib_tohops", 0),
    ]


class Ping(Packet):
    name = "Ping Contract"
    fields_desc = [
        ShortField("contract_type", 3),
        # 0 for request, 1 for response
        ShortField("code", 0),
        ShortField("hops", 255),
        # timestamp in microseconds. 8bytes
        LongField("timestamp", 0),
    ]


bind_layers(Ether, NewIPOffset, type=0x88B6)
