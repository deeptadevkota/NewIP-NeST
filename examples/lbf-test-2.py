# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @bhaskar792

# This program sends the LBF contract packet from h1 to h2
# with min delay as 500ms and max delay as 800ms
# it saves the pcap file generated at the sender's interface (h1_r1) in the pcap directory.
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

from New_IP.setup import Setup
from New_IP.sender import Sender
from New_IP.newip_hdr import LatencyBasedForwarding
import os
import time


if not os.path.isfile("LBF-testing-pcap/test1-5p-lbf.pcap"):
    os.system("sudo python3 pcap_gen_file2.py")
    time.sleep(5)

# in seconds
timeout = 10

setup_obj = Setup(resultsFolder="Test2")
bottleneck_queue_len = 100
setup_obj.setup_topology(buildLbf=False, bottleneck_queue_len=bottleneck_queue_len)
setup_obj.start_receiver(timeout=timeout, verbose=2)
setup_obj.get_tc_stats(interfaces=["r1_r2"], timeout=timeout)
# setup_obj.generate_pcap(interfaces=["h1_r1"], timeout=4)
# num_packets = [10,20,50,100,200,500,1000, 2000]
speeds = [0.001, 0.01, 0.1, 1, 10, 100, 500, 1000]
num_packets = [100]
# speeds= [1, 10, 100, 1000, 10000, 50000]
failsafe_timeout = 10
for speed in speeds:
    for num_packet in num_packets:
        with setup_obj.h1:
            num_packet = int(num_packet / 5)
            os.system(
                f"sudo timeout {failsafe_timeout} tcpreplay --mbps={speed} -q --loop={num_packet} -i 'h1_r1' LBF-testing-pcap/test1-5p-lbf.pcap "
            )
            time.sleep(1.5)


setup_obj.show_stats()
