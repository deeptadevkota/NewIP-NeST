/* SPDX-License-Identifier: GPL-2.0-only
   Copyright (c) 2019-2022 @bhaskar792 @rohitmp */
#include <linux/types.h>

struct newip_offset
{
    __u8 shipping_offset;
    __u8 contract_offset;
    __u8 payload_offset;
};

struct shipping_spec
{
    __u8 src_addr_type;
    __u8 dst_addr_type;
    __u8 addr_cast;
};
// src and dst are accessed outside the struct

struct max_delay_forwarding
{
    __u16 contract_type;
    __u16 max_allowed_delay;
    __u16 delay_exp;
};

struct ping_contract
{
    __u16 contract_type;
    __u16 code;
    __u16 hops;
    __u64 timestamp;
};

struct latency_based_forwarding
{
    __u16 contract_type;
    __u16 min_delay;
    __u16 max_delay;
    __u16 experienced_delay;
    __u16 fib_todelay;
    __u16 fib_tohops;
};

struct meta_info
{
    __u32 ifindex;
    struct max_delay_forwarding contract;
};