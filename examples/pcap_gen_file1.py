# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @bhaskar792


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
from New_IP.newip_hdr import LatencyBasedForwarding
import os
import time

timeout = 5

setup_obj = Setup()
setup_obj.setup_topology(buildLbf=False)
setup_obj.start_receiver(timeout= timeout)
# setup_obj.get_tc_stats(interfaces=["r1_r2"],timeout=timeout)
setup_obj.generate_pcap(interfaces=["h1_r1"], timeout=timeout,dir_name="LBF-testing-pcap")

with setup_obj.h1:
    os.system(f"tc qdisc replace dev h1_r1 root pfifo")
    sender_obj = Sender()

    sender_obj.make_packet(
        src_addr_type="ipv4",
        src_addr="10.0.1.2",
        dst_addr_type="ipv4",
        dst_addr="10.0.2.2",
        content="pkt 1 --- ipv4 to ipv6 from h1 to h2 more latency",
    )
    for i in range(0,10,1):
        lbf_contract = LatencyBasedForwarding(min_delay = 3000, max_delay = 4000, fib_todelay = 0, fib_tohops = 3)
        sender_obj.set_contract ([lbf_contract])
        sender_obj.send_packet(iface="h1_r1",count = 1)
os.rename('LBF-testing-pcap/h1_r1.pcap', 'LBF-testing-pcap/test1-10p-lbf-bulk.pcap')
