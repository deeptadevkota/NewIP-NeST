# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @bhaskar792

import argparse
import os
import json


class arg_parser:
    def __init__(self):
        self.set_args()
        self.parse_args()

    def set_args(self):
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument(
            "--tshark-path", "-tp", required=True, help="Tshark path"
        )
        self.parser.add_argument("--pcap-path", "-pp", required=True, help="Pcap path")

    def parse_args(self):
        args = self.parser.parse_args()
        self.tshark = args.tshark_path
        self.pcap = args.pcap_path


args = arg_parser()
tshark_path = args.tshark
pcap_path = args.pcap

os.system(f"{tshark_path} -r {pcap_path} -T json > tshark.json")
os.system(f"{tshark_path} -r {pcap_path} > tshark.txt")

tshark_file = open("tshark.json")
data = json.load(tshark_file)
res_file = open("tshark.txt")
result_list = res_file.readlines()

for i in range(len(result_list)):
    try:
        min_delay = data[i]["_source"]["layers"]["New IP Packet"][
            "Latency Based Forwarding Contract"
        ]["newip.lbfcontract.min_delay"]
        max_delay = data[i]["_source"]["layers"]["New IP Packet"][
            "Latency Based Forwarding Contract"
        ]["newip.lbfcontract.max_delay"]
        experienced_delay = data[i]["_source"]["layers"]["New IP Packet"][
            "Latency Based Forwarding Contract"
        ]["newip.lbfcontract.delay_exp"]
        experienced_delay = str(float(experienced_delay) / 10)
        payload = bytes.fromhex(
            str(
                data[i]["_source"]["layers"]["data"]["data.data"].replace(":", "")[0:16]
            )
        ).decode("utf-8")
    except:
        min_delay = ""
        max_delay = ""
        experienced_delay = ""
        payload = ""

    split_list = result_list[i].split("New IP", 1)
    result_list[i] = (
        split_list[0]
        + " lbf.min: "
        + min_delay
        + "ms lbf.max: "
        + max_delay
        + "ms lbf.exp: "
        + experienced_delay
        + "ms payload: "
        + payload
        + " "
        + split_list[1]
    )
    print(result_list[i])
