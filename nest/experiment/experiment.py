# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""User API to setup and run experiments on a given topology"""

import copy
import logging
from collections import defaultdict
import random
from nest.input_validator.metric import Bandwidth
from nest.network_utilities import ipv6_dad_check
from nest.input_validator import input_validator
from nest.topology import Node, Address
from nest.topology.interface import BaseInterface
from .run_exp import run_experiment
from .pack import Pack
from .tools import Iperf3Options

logger = logging.getLogger(__name__)

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
class Flow:
    """Defines a flow in the topology"""

    # pylint: disable=too-many-arguments
    @input_validator
    def __init__(
        self,
        source_node: Node,
        destination_node: Node,
        destination_address: Address,
        start_time: int,
        stop_time: int,
        number_of_streams: int,
    ):
        """
        'Flow' object in the topology

        Parameters
        ----------
        source_node : Node
            Source node of flow
        destination_node : Node
            Destination node of flow
        destination_address : Address/str
            Destination address of flow
        start_time : int
            Time to start flow (in seconds)
        stop_time : int
            Time to stop flow (in seconds)
        number_of_streams : int
            Number of streams in the flow
        """
        self.source_node = source_node
        self.destination_node = destination_node
        self.destination_address = destination_address
        self.start_time = start_time
        self.stop_time = stop_time
        self.number_of_streams = number_of_streams

        self._options = {"protocol": "TCP", "cong_algo": "cubic"}
        self.user_input_options = {}

    @property
    def destination_address(self):
        """Getter for destination address"""
        return self._destination_address

    @destination_address.setter
    def destination_address(self, destination_address):
        """Setter for destination address"""
        if isinstance(destination_address, str):
            destination_address = Address(destination_address)
        self._destination_address = destination_address

    def _get_props(self):
        """
        Get flow properties.

        NOTE: To be used internally
        """

        return [
            self.source_node.id,
            self.destination_node.id,
            self.destination_address.get_addr(with_subnet=False),
            self.start_time,
            self.stop_time,
            self.number_of_streams,
            self._options,
        ]

    def __repr__(self):
        classname = self.__class__.__name__
        return (
            f"{classname}({self.source_node!r}, {self.destination_node!r},"
            f" {self.destination_address!r}), {self.start_time!r}, {self.stop_time!r}"
            f" {self.number_of_streams!r})"
        )


class CoapFlow(Flow):
    """Defines a CoAP flow in the topology"""

    # pylint: disable=too-many-arguments
    @input_validator
    def __init__(
        self,
        source_node: Node,
        destination_node: Node,
        destination_address: Address,
        n_con_msgs: int,
        n_non_msgs: int,
        user_options=None,
    ):
        """
        Flow object representing CoAP flows in the topology.
        Inherited from the `Flow` class.

        Parameters
        ----------
        source_node : Node
            Source node of flow
        destination_node : Node
            Destination node of flow
        destination_address : Address/str
            Destination address of flow
        n_con_msgs : int
            Number of confimable messages to be sent in the flow
        n_non_msgs : int
            Number of non-confimable messages to be sent in the flow
        user_options : dict, optional
            User specified options for particular tools
        """
        self.source_node = source_node
        self.destination_node = destination_node
        self.destination_address = destination_address
        self.n_con_msgs = n_con_msgs
        self.n_non_msgs = n_non_msgs

        # Options for users to set
        self.user_options = user_options

        # Since start time, stop time and number of streams are needed for
        # initializing the parent class, we need to provide dummy values
        # for these members.
        super().__init__(source_node, destination_node, destination_address, 0, 0, 0)

    # Destination address getter and setter are implemented
    # in the Flow class which is the superclass of CoapFlow class

    def _get_props(self):
        """
        Get flow properties.

        NOTE: To be used internally
        """

        return [
            self.source_node.id,
            self.destination_node.id,
            self.destination_address.get_addr(with_subnet=False),
            self.n_con_msgs,
            self.n_non_msgs,
            self.user_options,
        ]

    def __repr__(self):
        classname = self.__class__.__name__
        return (
            f"{classname}({self.source_node!r}, {self.destination_node!r},"
            f" {self.destination_address!r}),"
            f" {self.n_con_msgs!r}, {self.n_non_msgs!r}, {self.user_options!r})"
        )


class NonLbfFlow:
    @input_validator
    def __init__(
        self,
        src_node: Node,
        dst_node: Node,
        src_addr_type: str,
        src_addr: str,
        dst_addr_type: str,
        dst_addr: str,
        pkt_count: int,
    ):
        self.src_node = src_node
        self.dst_node = dst_node
        self.src_addr_type = src_addr_type
        self.src_addr= src_addr
        self.dst_addr_type = dst_addr_type
        self.dst_addr = dst_addr
        self.pkt_count = pkt_count

    def _get_props(self):
        """
        Get flow properties.

        NOTE: To be used internally
        """

        return [
            self.src_node,
            self.dst_node,
            self.src_addr_type,
            self.src_addr,
            self.dst_addr_type,
            self.dst_addr,
            self.pkt_count,
        ]


class LbfFlow:
    @input_validator
    def __init__(
        self,
        src_node: Node,
        dst_node: Node,
        src_addr_type: str,
        src_addr: str,
        dst_addr_type: str,
        dst_addr: str,
        pkt_count: int,
        min_delay : int,
        max_delay : int,
        hops : int
    ):
        self.src_node = src_node
        self.dst_node = dst_node
        self.src_addr_type = src_addr_type
        self.src_addr= src_addr
        self.dst_addr_type = dst_addr_type
        self.dst_addr = dst_addr
        self.pkt_count = pkt_count
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.hops = hops

    def _get_props(self):
        """
        Get flow properties.

        NOTE: To be used internally
        """

        return [
            self.src_node,
            self.dst_node,
            self.src_addr_type,
            self.src_addr,
            self.dst_addr_type,
            self.dst_addr,
            self.pkt_count,
            self.min_delay,
            self.max_delay,
            self.hops
        ]


class Experiment:
    """Handles experiment to be run on topology"""

    # Stores configuration of old and new congestion algorithms for cleanup
    old_cong_algos = defaultdict(dict)
    new_cong_algos = []

    @input_validator
    def __init__(self, name: str):
        """
        Create experiment

        Parameters
        ----------
        name : str
            Name of experiment
        """
        self.name = name
        self.flows = []
        self.coap_flows = []
        self.non_lbf_flows = []
        self.lbf_flows = []
        self.node_stats = []
        self.qdisc_stats = []
        self.tcp_module_params = defaultdict(dict)

    def add_flow(self, flow):
        """
        Add flow to experiment
        By default, the flow is assumed to be
        TCP with cubic congestion algorithm

        Parameters
        ----------
        flow : Flow
            Add flow to experiment
        """
        self.flows.append(copy.deepcopy(flow))

    @input_validator
    def add_tcp_flow(self, flow: Flow, congestion_algorithm="cubic"):
        """
        Add TCP flow to experiment. If no congestion control algorithm
        is specified, then by default cubic is used.

        Note: The congestion control algorithm specified in this API
        overrides the congestion control algorithm specified in
        `topology.Node.configure_tcp_param()` API.

        Parameters
        ----------
        flow : Flow
            Flow to be added to experiment
        congestion_algorithm : str
            TCP congestion algorithm (Default value = 'cubic')
        """

        congestion_algo_list = [
            "bbr",
            "bic",
            "cdg",
            "cubic",
            "dctcp",
            "highspeed",
            "htcp",
            "illinois",
            "reno",
            "scalable",
            "vegas",
            "veno",
            "westwood",
            "yeah",
        ]

        if congestion_algorithm not in congestion_algo_list:
            raise ValueError(
                f"{congestion_algorithm} is not a valid TCP Congestion Control algorithm"
            )

        # TODO: Verify congestion algorithm

        options = {"protocol": "TCP", "cong_algo": congestion_algorithm}

        flow._options = options  # pylint: disable=protected-access
        self.add_flow(flow)

    @input_validator
    def add_udp_flow(
        self,
        flow: Flow,
        target_bandwidth: Bandwidth = Bandwidth("1mbit"),
        server_options: dict = None,
        client_options: dict = None,
    ):
        """
        Add UDP flow to experiment

        Parameters
        ----------
        flow : Flow
            Flow to be added to experiment
        target_bandwidth :
            UDP bandwidth (in Mbits) (Default value = '1mbit')
            This bandwidth limit is for each UDP stream in the flow
        """
        options = {"protocol": "udp", "target_bw": target_bandwidth.string_value}

        # options update with user configuration
        user_options = {}
        if server_options:
            user_options.update(server_options)
        if client_options:
            user_options.update(client_options)

        iperf3options = Iperf3Options(kwargs=user_options).getter()

        if "port_no" not in iperf3options:
            iperf3options.update({"port_no": random.randrange(1024, 65536)})

        iperf3options.update(options)

        # pylint: disable=protected-access
        flow._options = iperf3options
        self.add_flow(flow)

    @input_validator
    def add_coap_flow(self, coap_flow: CoapFlow):
        """
        Add a CoAP flow to experiment

        Parameters
        ----------
        coap_flow : CoapFlow
            The coap flow to be added to experiment
        """
        self.coap_flows.append(copy.deepcopy(coap_flow))

    @input_validator
    def add_non_lbf_flow(self, non_lbf_flow: NonLbfFlow):
        self.non_lbf_flows.append(copy.deepcopy(non_lbf_flow))

    @input_validator
    def add_lbf_flow(self, lbf_flow: LbfFlow):
        self.lbf_flows.append(copy.deepcopy(lbf_flow))

    @input_validator
    def require_qdisc_stats(self, interface: BaseInterface, stats=""):
        """
        Stats to be obtained from qdisc in interface

        Parameters
        ----------
        interface : BaseInterface
            Interface containing the qdisc
        stats : list(str)
            Stats required (Default value = '') [NOT SUPPORTED]
        """
        # TODO: Leads to rewrite if the function is called
        # twice with same 'interface'

        # for stat in stats:
        #     if stat not in Experiment.qdisc_stats:
        #         raise ValueError('{} is not a valid Queue property.'.format(stat))

        if interface.get_qdisc() is None:
            raise ValueError("Given interface hasn't been assigned any qdisc.")

        self.qdisc_stats.append(
            {
                "ns_id": interface.node_id,
                "int_id": interface.ifb_id,
                "qdisc": interface.get_qdisc().qdisc,
                "stats": stats,
            }
        )

    def configure_tcp_module_params(self, congestion_algorithm, **kwargs):
        """
        Set TCP module parameters

        Parameters
        ----------
        congestion_algorithm : str
            TCP congestion algorithm
        **kwargs :
            module parameters to set
        """
        self.tcp_module_params[congestion_algorithm].update(kwargs)
        logger.info("TCP module parameters will be set when the experiment is run")

    @ipv6_dad_check
    def run(self):
        """Run the experiment"""
        print()
        logger.info("Running experiment %s ", self.name)
        Pack.init(self.name)
        # if non lbf flows exist then
        run_experiment(self)

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}({self.name!r})"
