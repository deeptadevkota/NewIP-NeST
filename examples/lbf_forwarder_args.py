import argparse


class lbf_forwarder_args:
    def __init__(self):
        self.set_args()
        self.parse_args()

    def set_args(self):
        self.parser = argparse.ArgumentParser()
        # Add long and short argument
        # example -i h1_r1 -st 8b -dt 8b -da h1 -sa h3 -s 30  -c 10
        # self.parser.add_argument("--interface", "-i", required=True,
        #                     help="set source address type")               Not required as we are specifying the src host and we only have 1 interface
        self.parser.add_argument("--ping", "-p", action="store_true", default=False)
        self.parser.add_argument(
            "--src-type",
            "-st",
            nargs="+",
            default=["ipv4"],
            help="set source address types",
        )
        self.parser.add_argument(
            "--src",
            "-sa",
            nargs="+",
            default=["h1"],
            help="set source hosts",
        )
        self.parser.add_argument(
            "--dst-type",
            "-dt",
            nargs="+",
            default=["ipv4"],
            help="set dst address types",
        )
        self.parser.add_argument(
            "--dst",
            "-da",
            nargs="+",
            default=["h2"],
            help="set destination hosts",
        )
        self.parser.add_argument(
            "--lbf-contract",
            "-lbf",
            nargs="*",
            help="Use lbf contract with min and max delay. usage -lbf min_delay max_delay",
        )
        self.parser.add_argument(
            "--legacy_ip",
            "-li",
            action="store_true",
            default=False,
            help="Send a legacy packet to destination",
        )
        self.parser.add_argument(
            "--no-lbf",
            "-nolbf",
            action="store_true",
            default=False,
            help="Send a packet without lbf to destination",
        )
        self.parser.add_argument(
            "--timeout",
            "-t",
            type=int,
            default=10,
            help="timeout for receiver and pcap capture",
        )
        self.parser.add_argument(
            "--show-packet",
            "-sp",
            action="store_true",
            default=False,
            help="Show Packet",
        )
        self.parser.add_argument(
            "--pkt-count", "-c", type=int, default=1, help="number of pkts to send"
        )
        self.parser.add_argument(
            "--pkt-size", "-s", type=int, default=100, help="pkt size"
        )
        self.parser.add_argument(
            "--pcap-file",
            "-pf",
            default="",
            help="pcap file to be replayed, use with -tr",
        )

        self.parser.add_argument(
            "--pcap-all",
            "-pa",
            action="store_true",
            default=False,
            help="Capture pcap for all nodes",
        )
        self.parser.add_argument(
            "--pcap-dst",
            "-pd",
            action="store_true",
            default=False,
            help="Capture pcap for dst node",
        )
        self.parser.add_argument(
            "--pcap-interface-list",
            "-pil",
            action="append",
            default=None,
            help="Capture packets on this list of interface",
        )
        self.parser.add_argument(
            "--pcap-node-list",
            "-pnl",
            action="append",
            default=None,
            help="Capture packets on this list of nodes",
        )

        self.parser.add_argument(
            "--tcp-replay",
            "-tr",
            action="store_true",
            default=False,
            help="Use tcp-replay to send the packets",
        )
        # self.parser.add_argument("--limit",    "-lmt",   type=int,
        #                     default=100000,
        #                     help="limit the number of packets to be sent, use with --tcp-replay=true")
        self.parser.add_argument(
            "--loop",
            "-l",
            type=int,
            default=1,
            help="loop through the pcap file, use with --tcp-replay=true",
        )

        self.group = self.parser.add_mutually_exclusive_group()
        self.group.add_argument(
            "--packets-per-sec",
            "-pps",
            type=int,
            default=100,
            help="send given number of packets per second, use with --tcp-replay=true",
        )
        self.group.add_argument(
            "--Mbps",
            "-mbps",
            type=int,
            default=0,
            help="send at the specified rate in Mbps, use with --tcp-replay=true",
        )
        self.group.add_argument(
            "--topspeed",
            "-ts",
            action="store_true",
            default=False,
            help="send at the maximum rate, use with --tcp-replay=true",
        )

        self.parser.add_argument(
            "--statistics",
            "-stats",
            type=int,
            default=10,
            help="print stats after every given second, use with --tcp-replay=true",
        )

    def parse_args(self):
        # Read arguments from the command line
        args = self.parser.parse_args()
        valid_address_types = ["ipv4", "ipv6", "8bit"]
        self.src_addr_type = list(set(args.src_type))
        for addr_type in self.src_addr_type:
            if addr_type not in valid_address_types:
                self.parser.error("src address should be from ipv4, ipv6 or 8bit")

        self.dst_addr_type = args.dst_type
        for addr_type in self.dst_addr_type:
            if addr_type not in valid_address_types:
                self.parser.error("dst address should be from ipv4, ipv6 or 8bit")

        valid_hosts = ["h1", "h2", "h3"]
        self.src = list(set(args.src))
        for host in self.src:
            if host not in valid_hosts:
                self.parser.error("dst address should be from h1, h2 or h3")

        self.dst = list(set(args.dst))
        for host in self.dst:
            if host not in valid_hosts:
                self.parser.error("dst address should be from h1, h2 or h3")
        if (args.lbf_contract is not None) and ((len(args.lbf_contract) % 2) != 0):
            self.parser.error(
                "Either give no values for contract, or multiple of two, not {}.".format(
                    len(args.lbf_contract)
                )
            )

        self.ping = args.ping
        self.lbfList = args.lbf_contract
        self.legacy_ip = args.legacy_ip
        self.no_lbf = args.no_lbf
        self.packet_types = []
        if self.ping:
            self.packet_types.append("ping")
        if self.legacy_ip:
            self.packet_types.append("li")
        if self.lbfList != None:
            self.packet_types.append("lbf")
        if self.no_lbf or self.packet_types == []:
            self.packet_types.append("nolbf")
        self.timeout = args.timeout
        self.showPacket = args.show_packet
        self.pktCount = args.pkt_count
        self.pktSize = args.pkt_size
        self.pcap = args.pcap_file

        self.pcapAll = args.pcap_all
        self.pcapDst = args.pcap_dst
        self.pcapNodeList = args.pcap_node_list
        self.pcapInterfaceList = args.pcap_interface_list

        self.useTcpReplay = args.tcp_replay
        # self.trLimit = args.limit
        self.trLoop = args.loop
        self.trPps = args.packets_per_sec
        self.trMbps = args.Mbps
        self.trTopspeed = args.topspeed
        self.trStats = args.statistics

        self.size = args.pkt_size
        self.count = args.pkt_count
