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

from distutils.core import setup
from New_IP.setup import Setup
from New_IP.sender import Sender
from New_IP.newip_hdr import LatencyBasedForwarding
import os
import time

if not os.path.isfile("LBF-testing-pcap/test1-5p-lbf.pcap"):
    print("generating 5p file")
    os.system("sudo python3 pcap_gen_file2.py")
if not os.path.isfile("LBF-testing-pcap/test1-10p-lbf-bulk.pcap"):
    print("generating 10p file")
    os.system("sudo python3 pcap_gen_file1.py")
# in seconds
timeout = 50

setup_obj = Setup(resultsFolder="Test1")
bottleneck_queue_len = 100
setup_obj.setup_topology(buildLbf=False, bottleneck_queue_len=bottleneck_queue_len)
setup_obj.start_receiver(timeout=timeout, verbose=2)
setup_obj.get_tc_stats(interfaces=["r1_r2"], timeout=timeout)
# setup_obj.generate_pcap(interfaces=["h1_r1"], timeout=4)

timeout = 2
with setup_obj.h1:

    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={int(1 * (bottleneck_queue_len/100))} -i 'h1_r1' LBF-testing-pcap/test1-10p-lbf-bulk.pcap "
    )
    time.sleep(0.5)
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={1} -i 'h1_r1' LBF-testing-pcap/test1-5p-lbf.pcap "
    )
    time.sleep(3)

    # 4s
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={int(3 * (bottleneck_queue_len/100))} -i 'h1_r1' LBF-testing-pcap/test1-10p-lbf-bulk.pcap "
    )
    time.sleep(0.5)
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={1} -i 'h1_r1' LBF-testing-pcap/test1-5p-lbf.pcap "
    )
    time.sleep(3)

    # 8s
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={int(5 * (bottleneck_queue_len/100))} -i 'h1_r1' LBF-testing-pcap/test1-10p-lbf-bulk.pcap "
    )
    time.sleep(0.5)
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={1} -i 'h1_r1' LBF-testing-pcap/test1-5p-lbf.pcap "
    )
    time.sleep(3)

    # 12s
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={int(7 * (bottleneck_queue_len/100))} -i 'h1_r1' LBF-testing-pcap/test1-10p-lbf-bulk.pcap "
    )
    time.sleep(0.5)
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={1} -i 'h1_r1' LBF-testing-pcap/test1-5p-lbf.pcap "
    )
    time.sleep(3)

    # 16s
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={int(8 * (bottleneck_queue_len/100))} -i 'h1_r1' LBF-testing-pcap/test1-10p-lbf-bulk.pcap "
    )
    time.sleep(0.5)
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={1} -i 'h1_r1' LBF-testing-pcap/test1-5p-lbf.pcap "
    )
    time.sleep(3)

    # 20s
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={int(9 * (bottleneck_queue_len/100))} -i 'h1_r1' LBF-testing-pcap/test1-10p-lbf-bulk.pcap "
    )
    time.sleep(0.5)
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={1} -i 'h1_r1' LBF-testing-pcap/test1-5p-lbf.pcap "
    )
    time.sleep(3)

    # 24s
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={int(10 * (bottleneck_queue_len/100))} -i 'h1_r1' LBF-testing-pcap/test1-10p-lbf-bulk.pcap "
    )
    time.sleep(0.5)
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={1} -i 'h1_r1' LBF-testing-pcap/test1-5p-lbf.pcap "
    )
    time.sleep(3)

    # 28s
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={int(20 * (bottleneck_queue_len/100))} -i 'h1_r1' LBF-testing-pcap/test1-10p-lbf-bulk.pcap "
    )
    time.sleep(0.5)
    os.system(
        f"sudo timeout {timeout} tcpreplay --mbps=0.1 -q --loop={1} -i 'h1_r1' LBF-testing-pcap/test1-5p-lbf.pcap "
    )
    time.sleep(3)


# setup_obj.show_stats()
