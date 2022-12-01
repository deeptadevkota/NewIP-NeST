# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @bhaskar792

# This program sends the New-IP packet from h1 to h2
# The source address type is ipv4
# The destination address type is ipv6


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

setup_obj = Setup()
setup_obj.setup_topology()
setup_obj.start_receiver()

with setup_obj.h1:
    sender_obj = Sender()

    # IPv4 to IPv6
    sender_obj.make_packet(
        src_addr_type="ipv4",
        src_addr="10.0.1.2",
        dst_addr_type="ipv6",
        dst_addr="10::2:2",
        content="ipv4 to ipv6 from h1 to h2",
    )
    # 
    sender_obj.send_packet(iface="h1_r1", show_pkt=True)

    

# setup_obj.show_stats()
