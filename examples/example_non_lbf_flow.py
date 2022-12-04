# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.experiment.experiment import NonLbfFlow
from nest.experiment import *
from New_IP.setup import Setup

exp = Experiment("non-lbf-flow-experiment")
flow3 = NonLbfFlow(["h1"], ["h2"], ['ipv4'], ['ipv6'], 10, 10)
exp.add_non_lbf_flow(flow3)
exp.run()

