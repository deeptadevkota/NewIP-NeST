from nest.experiment.experiment import NonLbfFlow
from nest.experiment import *
from New_IP.setup import Setup


setup_obj = Setup()

# setting up the Topology
setup_obj.setup_topology()

# Defining New-IP contract less flows
flow1 = NonLbfFlow(
    src_node=setup_obj.h1,
    dst_node=setup_obj.h3,
    src_addr_type="ipv4",
    src_addr=setup_obj.info_dict[setup_obj.h1.name]["ipv4"],
    dst_addr_type="ipv6",
    dst_addr=setup_obj.info_dict[setup_obj.h3.name]["ipv6"],
    pkt_count=5,
)

flow2 = NonLbfFlow(
    src_node=setup_obj.h1,
    dst_node=setup_obj.h2,
    src_addr_type="ipv6",
    src_addr=setup_obj.info_dict[setup_obj.h1.name]["ipv6"],
    dst_addr_type="ipv6",
    dst_addr=setup_obj.info_dict[setup_obj.h2.name]["ipv6"],
    pkt_count=10,
)


# Defining UDP flow from h1 to h3
flow3 = Flow(
    source_node=setup_obj.h1,
    destination_node=setup_obj.h3,
    destination_address=setup_obj.info_dict[setup_obj.h3.name]["ipv4"],
    start_time=0,
    stop_time=10,
    number_of_streams=1,
)

# Defining TCP BBR flow from h1 to h2
flow4 = Flow(
    source_node=setup_obj.h1,
    destination_node=setup_obj.h2,
    destination_address=setup_obj.info_dict[setup_obj.h2.name]["ipv4"],
    start_time=0,
    stop_time=10,
    number_of_streams=1,
)


# instantiating the Experiment class of NeST
exp = Experiment(name="non-lbf-flow with TCP and UDP  ")

# Adding New-IP contract less flows
exp.add_non_lbf_flow(flow1)
exp.add_non_lbf_flow(flow2)

# Adding UDP flow
exp.add_udp_flow(flow3, target_bandwidth="12mbit")

# Adding TCP flow
exp.add_tcp_flow(flow4, "bbr")

# Running the experiment for all added flows
exp.run()
