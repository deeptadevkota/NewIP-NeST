
from nest.experiment.experiment import NonLbfFlow
from nest.experiment import *
from New_IP.setup import Setup
import copy


class NewIP:
    def __init__(self) -> None:
        pass

    non_lbf_flows = []
    topo = None

    def create_topology(self):
        topo = Setup()
        topo.setup_topology()
        self.topo = topo

    def add_non_lbf_flows(self, non_lbf_flow):
        self.non_lbf_flows.append(copy.deepcopy(non_lbf_flow))



newip_obj = NewIP()

# setting up the Topology
newip_obj.create_topology()



# Defining New-IP contract less flows
flow1 = NonLbfFlow(src_node=newip_obj.topo.h1, dst_node=newip_obj.topo.h3,
                   src_addr_type="ipv4", dst_addr_type="ipv6", pkt_count=5)
flow2 = NonLbfFlow(src_node=newip_obj.topo.h1, dst_node=newip_obj.topo.h2,
                   src_addr_type="ipv4", dst_addr_type="ipv6", pkt_count=10)
flow3 = NonLbfFlow(src_node=newip_obj.topo.h1, dst_node=newip_obj.topo.h3,
                   src_addr_type="ipv6", dst_addr_type="ipv6", pkt_count=3)
flow4 = NonLbfFlow(src_node=newip_obj.topo.h1, dst_node=newip_obj.topo.h2,
                   src_addr_type="ipv6", dst_addr_type="ipv6", pkt_count=5)

# adding NewIP contract less flows to the NewIP class
newip_obj.add_non_lbf_flows(flow1)
newip_obj.add_non_lbf_flows(flow2)
newip_obj.add_non_lbf_flows(flow3)
newip_obj.add_non_lbf_flows(flow4)


# instantiating the Experiment class of NeST
exp = Experiment(
    name="non-lbf-flow-experiment",
    non_lbf_flows=newip_obj.non_lbf_flows,
    topo=newip_obj.topo,
)



# Defining UDP flow from h1 to h3
flow5 = Flow(source_node=newip_obj.topo.h1, destination_node=newip_obj.topo.h3,
             destination_address=newip_obj.topo.info_dict[newip_obj.topo.h3.name]['ipv4'], 
             start_time=0, stop_time=10, number_of_streams=1)

# Defining TCP BBR flow from h1 to h2
flow6 = Flow(source_node=newip_obj.topo.h1, destination_node=newip_obj.topo.h2,
             destination_address=newip_obj.topo.info_dict[newip_obj.topo.h2.name]['ipv4'], 
             start_time=0, stop_time=10, number_of_streams=1)


# Adding UDP flow
exp.add_udp_flow(flow5, target_bandwidth="12mbit")

# Adding TCP flow
exp.add_tcp_flow(flow6, "bbr")

# Running the experiment for all added flows
exp.run()
