# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @bhaskar792

# This program sends the New-IP packet from h1 to h2
# The source address type is ipv4
# The destination address type is 8bit


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

from New_IP.setup import Setup
from New_IP.sender import Sender

setup_obj = Setup()
setup_obj.setup_topology()
setup_obj.start_receiver()

with setup_obj.h1:
    sender_obj = Sender()
    delay = 500

    sender_obj.make_packet(
        src_addr_type="ipv4",
        src_addr="10.0.1.2",
        dst_addr_type="8bit",
        dst_addr=0b11,
        content="8bit to ipv4 from h1 to h3",
    )
    sender_obj.send_packet(iface="h1_r1")

setup_obj.show_stats()
