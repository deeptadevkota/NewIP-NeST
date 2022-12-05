# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
import copy
from nest.experiment.experiment import NonLbfFlow
from nest.experiment import *
from New_IP.setup import Setup


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
newip_obj.create_topology()
flow1 = NonLbfFlow(newip_obj.topo.h1, newip_obj.topo.h3, "ipv4", "ipv6", 5, 5)
flow2 = NonLbfFlow(newip_obj.topo.h1, newip_obj.topo.h2, "ipv4", "ipv6", 5, 10)
flow3 = NonLbfFlow(newip_obj.topo.h1, newip_obj.topo.h3, "ipv4", "ipv6", 5, 3)


newip_obj.add_non_lbf_flows(flow1)
newip_obj.add_non_lbf_flows(flow2)
newip_obj.add_non_lbf_flows(flow3)


exp = Experiment(
    name="non-lbf-flow-experiment",
    non_lbf_flows=newip_obj.non_lbf_flows,
    topo=newip_obj.topo,
)
exp.run()


#
