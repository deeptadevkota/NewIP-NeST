/* SPDX-License-Identifier: GPL-2.0-only
   Copyright (c) 2019-2022 @bhaskar792 @rohitmp */
#include <linux/bpf.h>
#include <linux/in.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

// The parsing helper functions from the packet01 lesson have moved here
#include "../common/parsing_helpers.h"
#include "../common/rewrite_helpers.h"

/* Defines xdp_stats_map */
#include "../common/xdp_stats_kern_user.h"
#include "../common/xdp_stats_kern.h"

#include "newip.h"
#include <stdio.h>

#ifndef AF_INET
#define AF_INET 1
#endif

#ifndef AF_INET6
#define AF_INET6 6
#endif


#ifndef memcpy
#define memcpy(dest, src, n) __builtin_memcpy((dest), (src), (n))
#endif

struct bpf_map_def SEC("maps") static_redirect_8b = {
	.type = BPF_MAP_TYPE_HASH,
	.key_size = sizeof(__u8),
	.value_size = sizeof(__u32),
	.max_entries = 256,
};

#define IPV6_FLOWINFO_MASK bpf_htonl(0x0FFFFFFF)

#define ETH_P_NEWIP 0x88b6
#define NEWIP_T_IPv4 0x00
#define NEWIP_T_IPv6 0x01
#define NEWIP_T_8b 0x02

// static __always_inline int parse_contract_spec(void *contract, void *data_end, struct meta_info *meta)
// {
// }

SEC("xdp_router")
int xdp_router_func(struct xdp_md *ctx)
{
	struct meta_info *meta;
	int ret;
	ret = bpf_xdp_adjust_meta(ctx, -(int)sizeof(*meta));
	if (ret < 0)
	{
		return XDP_ABORTED;
	}
	void *data_end = (void *)(long)ctx->data_end;
	void *data = (void *)(long)ctx->data;
	struct bpf_fib_lookup fib_params = {};
	struct ethhdr *eth = data;
	struct shipping_spec *shipping_spec;
	struct newip_offset *newipoff;
	__u16 h_proto;
	__u64 nh_off;
	int rc;
	int action = XDP_PASS;

	nh_off = sizeof(*eth);
	if (data + nh_off > data_end)
	{
		action = XDP_DROP;
		goto out;
	}

	h_proto = eth->h_proto;
	if (h_proto == bpf_htons(ETH_P_NEWIP))
	{
		newipoff = data + nh_off;
		if (newipoff + 1 > data_end)
		{
			action = XDP_DROP;
			goto out;
		}
		shipping_spec = data + nh_off + newipoff->shipping_offset;
		if (shipping_spec + 1 > data_end)
		{
			action = XDP_DROP;
			goto out;
		}
		meta = (void *)(unsigned long)ctx->data_meta;
		if (meta + 1 > data)
		{
			return XDP_ABORTED;
		}
		// int val = shipping_spec->src_addr_type;
		// bpf_printk("src type: %d\n", val);
		// val = shipping_spec->dst_addr_type;
		// bpf_printk("dst type: %d\n", val);
		__u8 type_src = shipping_spec->src_addr_type;
		__u32 *newiphdr_v4_src;
		struct in6_addr *newiphdr_v6_src;
		__u8 *newiphdr_8b_src;
		int size = 0;
		if (type_src == NEWIP_T_IPv4)
		{
			size = sizeof(*newiphdr_v4_src);
		}
		else if (type_src == NEWIP_T_IPv6)
		{
			size = sizeof(*newiphdr_v6_src);
		}
		else if (type_src == NEWIP_T_8b)
		{
			size = sizeof(*newiphdr_8b_src);
		}
		__u8 type_dst = shipping_spec->dst_addr_type;

		if (type_dst == NEWIP_T_IPv4)
		{
			__u32 *newiphdr_v4_dst;
			newiphdr_v4_dst = data + nh_off + sizeof(*shipping_spec) + sizeof(*newipoff) + size;
			if (newiphdr_v4_dst + 1 > data_end)
			{
				action = XDP_DROP;
				goto out;
			}
			fib_params.family = AF_INET;
			fib_params.ipv4_dst = *newiphdr_v4_dst;
			// bpf_printk("v4 dst: %d\n", *newiphdr_v4_dst);
		}
		else if (type_dst == NEWIP_T_IPv6)
		{
			struct in6_addr *dst = (struct in6_addr *)fib_params.ipv6_dst;
			struct in6_addr *newiphdr_v6_dst;
			newiphdr_v6_dst = data + nh_off + sizeof(*shipping_spec) + sizeof(*newipoff) + size;
			if (newiphdr_v6_dst + 1 > data_end)
			{
				action = XDP_DROP;
				goto out;
			}
			fib_params.family = AF_INET6;

			*dst = *newiphdr_v6_dst;
		}
		else if (type_dst == NEWIP_T_8b)
		{ // Update metadata of Non-IP packets and return
			__u8 *newiphdr_8b_dst;
			newiphdr_8b_dst = data + nh_off + sizeof(*shipping_spec) + sizeof(*newipoff) + size;
			if (newiphdr_8b_dst + 1 > data_end)
			{
				action = XDP_DROP;
				goto out;
			}
			// bpf_printk("8b dst: %d\n",*newiphdr_8b_dst);
			__u32 *ifindex = bpf_map_lookup_elem(&static_redirect_8b, newiphdr_8b_dst);
			if (!ifindex)
			{
				bpf_printk("no ifindex\n");
				return XDP_ABORTED;
			}
			meta->ifindex = *ifindex;
		}
		else
		{
			action = XDP_DROP;
			goto out;
		}
		//process contract
		if (newipoff->contract_offset < newipoff->payload_offset)
		{
			__u16 *contract_ptr;
			__u16 contract_type;
			contract_ptr = data + nh_off + newipoff->contract_offset;
			if (contract_ptr + 1 > data_end)
			{
				action = XDP_DROP;
				goto out;
			}
			contract_type = bpf_ntohs(*contract_ptr);
			// bpf_printk ("contract type: %d\n", contract_type);
			if (contract_type == 3){
				// Ping contract
				struct ping_contract *ping;
				ping = (struct ping_contract *)contract_ptr;
				if (ping + 1 > data_end) {
					action = XDP_DROP;
					goto out;
				}
				// Reduce hop by one. 
				// Note: This will be done once per router
				ping->hops = bpf_htons(bpf_ntohs(ping->hops) - 1);
				// bpf_printk("Ping Code: %d       Hops: %d\n", bpf_ntohs(ping->code), bpf_ntohs(ping->hops));

			} else if (contract_type == 1) {
				struct max_delay_forwarding *mdf;
				mdf = (struct max_delay_forwarding *)contract_ptr;
				if(mdf + 1 > data_end){
					action = XDP_DROP;
					goto out;
				}
				meta->contract.max_allowed_delay = mdf->max_allowed_delay;
				meta->contract.delay_exp = mdf->delay_exp;
				// bpf_printk("max allowed delay: %d...delay_exp: %d\n", bpf_ntohs(meta->contract.max_allowed_delay), bpf_ntohs(meta->contract.delay_exp));
			}
		}
		if (type_dst == NEWIP_T_8b)
		{
			goto out;
		}
	}
	else
	{
		goto out;
	}

	// Just for packets with ip dst
	fib_params.ifindex = ctx->ingress_ifindex;
	rc = bpf_fib_lookup(ctx, &fib_params, sizeof(fib_params), 0);
	// bpf_printk("rc: %d\n", rc);
	switch (rc)
	{
	case BPF_FIB_LKUP_RET_SUCCESS: /* lookup successful */
		/* Only New-IP packets will reach this point */
		// bpf_printk("lookup successfull\n");
		memcpy(eth->h_dest, fib_params.dmac, ETH_ALEN);
		memcpy(eth->h_source, fib_params.smac, ETH_ALEN);
		meta->ifindex = fib_params.ifindex;
		// bpf_printk("ifindex: %d\n", fib_params.ifindex);
		action = XDP_PASS;
		break;
	case BPF_FIB_LKUP_RET_BLACKHOLE:   /* dest is blackholed; can be dropped */
	case BPF_FIB_LKUP_RET_UNREACHABLE: /* dest is unreachable; can be dropped */
	case BPF_FIB_LKUP_RET_PROHIBIT:	   /* dest not allowed; can be dropped */
		action = XDP_DROP;
		break;
	case BPF_FIB_LKUP_RET_NOT_FWDED:	/* packet is not forwarded */
		bpf_printk ("route not found, check if routing suite is working properly");
	case BPF_FIB_LKUP_RET_FWD_DISABLED: /* fwding is not enabled on ingress */
	case BPF_FIB_LKUP_RET_UNSUPP_LWT:	/* fwd requires encapsulation */
	case BPF_FIB_LKUP_RET_NO_NEIGH:		/* no neighbor entry for nh */
	case BPF_FIB_LKUP_RET_FRAG_NEEDED:	/* fragmentation required to fwd */
		/* PASS */
		break;
	}

out:

	return xdp_stats_record_action(ctx, action);
}

SEC("xdp_pass")
int xdp_pass_func(struct xdp_md *ctx)
{
	return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
