# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @bhaskar792

from New_IP.setup import Setup
from New_IP.sender import Sender

setup_obj = Setup()
setup_obj.setup_topology()
setup_obj.start_receiver()

with setup_obj.h1:
    sender_obj = Sender()
    delay = 500

    # IPv4 to IPv6
    sender_obj.make_packet(
        src_addr_type="ipv4",
        src_addr="10.0.1.2",
        dst_addr_type="ipv6",
        dst_addr="10::2:2",
        content="ipv4 to ipv6 from h1 to h2 more latency",
    )
    sender_obj.insert_contract(
        contract_type="latency_based_forwarding", params=[0, 800, 300, 3]
    )  # min_delay, max_delay, fib_todelay, fib_tohops
    sender_obj.send_packet(iface="h1_r1", show_pkt=True)

    sender_obj.make_packet(
        src_addr_type="ipv4",
        src_addr="10.0.1.2",
        dst_addr_type="ipv6",
        dst_addr="10::2:2",
        content="ipv4 to ipv6 from h1 to h2 more latency",
    )
    sender_obj.insert_contract(
        contract_type="latency_based_forwarding", params=[500, 800, 300, 3]
    )  # min_delay, max_delay, fib_todelay, fib_tohops
    sender_obj.send_packet(iface="h1_r1", show_pkt=True)

    sender_obj.make_packet(
        src_addr_type="ipv4",
        src_addr="10.0.1.2",
        dst_addr_type="ipv6",
        dst_addr="10::2:2",
        content="ipv4 to ipv6 from h1 to h2 less latency",
    )
    sender_obj.insert_contract(
        contract_type="latency_based_forwarding", params=[350, 380, 300, 3]
    )  # min_delay, max_delay, fib_todelay, fib_tohops
    sender_obj.send_packet(iface="h1_r1", show_pkt=True)

    sender_obj.make_packet(
        src_addr_type="ipv4",
        src_addr="10.0.1.2",
        dst_addr_type="ipv6",
        dst_addr="10::2:2",
        content="ipv4 to ipv6 from h1 to h2 much more latency",
    )
    sender_obj.insert_contract(
        contract_type="latency_based_forwarding", params=[2000, 5000, 300, 3]
    )  # min_delay, max_delay, fib_todelay, fib_tohops
    sender_obj.send_packet(iface="h1_r1", show_pkt=True)

    # # 8bit to 8bit
    sender_obj.make_packet(
        src_addr_type="8bit",
        src_addr=0b1,
        dst_addr_type="8bit",
        dst_addr=0b10,
        content="8bit to 8bit from h1 to h2",
    )
    sender_obj.insert_contract(contract_type="max_delay_forwarding", params=[delay])
    sender_obj.send_packet(iface="h1_r1")

    # # 8bit to IPv4
    sender_obj.make_packet(
        src_addr_type="8bit",
        src_addr=0b1,
        dst_addr_type="ipv4",
        dst_addr="10.0.3.2",
        content="8bit to ipv4 from h1 to h3",
    )
    sender_obj.insert_contract(
        contract_type="latency_based_forwarding", params=[500, 800, 300, 3]
    )  # min_delay, max_delay, fib_todelay, fib_tohops
    sender_obj.send_packet(iface="h1_r1")

    sender_obj.make_packet(
        src_addr_type="8bit",
        src_addr=0b1,
        dst_addr_type="ipv4",
        dst_addr="10.0.3.2",
        content="8bit to ipv4 from h1 to h3",
    )
    sender_obj.send_packet(iface="h1_r1")

    # IPv4 to IPv4
    sender_obj.make_packet(
        src_addr_type="ipv4",
        src_addr="10.0.1.2",
        dst_addr_type="ipv4",
        dst_addr="10.0.2.2",
        content="ipv4 to ipv4 from h1 to h2",
    )
    sender_obj.insert_contract(contract_type="max_delay_forwarding", params=[delay])
    sender_obj.send_packet(iface="h1_r1", show_pkt=True)


setup_obj.show_stats()
