# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @bhaskar792

# This program sends the LBF contract packet from h1 to h2
# with min delay as 50ms max delay as 60ms
# The source address type is ipv4
# The destination address type is ipv4


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

from time import sleep
from New_IP.setup import Setup
from New_IP.sender import Sender
from New_IP.newip_hdr import LatencyBasedForwarding
import os

setup_obj = Setup()
setup_obj.setup_topology()
setup_obj.start_receiver(timeout=5)

with setup_obj.h1:
    sender_obj = Sender()
    lbf_Contract = LatencyBasedForwarding(
        min_delay=50, max_delay=60, fib_todelay=0, fib_tohops=3
    )

    # IPv4 to IPv6
    sender_obj.make_packet(
        src_addr_type="ipv4",
        src_addr="10.0.1.2",
        dst_addr_type="ipv4",
        dst_addr="10.0.2.2",
        content="ipv4 to ipv4 from h1 to h2",
    )
    sender_obj.set_contract([lbf_Contract])
    # sleep(15)
    sender_obj.send_packet(iface="h1_r1", show_pkt=True)


# setup_obj.show_stats()
