// SPDX-License-Identifier: GPL-2.0-only
// Copyright (c) 2019-2022 @bhaskar792 @rohitmp @lesliemonis

// enqueue mdf packets in lbf queue
#include <linux/module.h>
#include <net/pkt_sched.h>

#include "newip.h"

#define ETH_P_NEWIP 0x88b6

#define LOGLEN 255
#define IFBITRATE 100000000

#define EARLYENTRIES 1
#define LATEENTRIES 2

#define DMAX_BESTEFFORT 10000
#define LQB_BESTEFFORT 64000

#define LQB_RANGE 10

struct lbf_params
{
};

struct lbf_vars
{
	__u16 hops_left;
};

struct lbf_stats
{
	psched_time_t delay;
	__u32 overlimit;
};

struct lbf_sched_data
{
	struct lbf_hnode_head* hnode_list;
	struct lbf_pnode* next_pnode;
	struct lbf_params params;
	struct lbf_vars vars;
	struct lbf_stats stats;
	struct qdisc_watchdog watchdog;
};

struct lbf_skb_cb
{
	int val;
	psched_time_t enqueue_time;
};
struct lbf_pnode
{
	struct lbf_pnode* next;
	struct lbf_hnode* hnode;   // only pnodes directly associated with hnodes will have hnodes
	__u64 tmin_nsec;
	__u64 tmax_nsec;
	__u64 trcv;
	struct sk_buff* realpkt;
};


struct lbf_hnode
{
	struct lbf_hnode * next_hnode;
	struct lbf_pnode * queue; 
	struct lbf_hnode * prev_hnode;
	int hnode_num;
	int range_start;
	int range_end;
};

struct lbf_hnode_head
{
	struct lbf_hnode * head;
	struct lbf_hnode * tail; 
	int len;
};

static void lbf_params_init(struct lbf_params *params)
{
}

static void lbf_vars_init(struct lbf_vars *vars)
{
}

static void lbf_stats_init(struct lbf_stats *stats)
{
	stats->delay = PSCHED_PASTPERFECT;
	stats->overlimit = 0;
}

static struct lbf_skb_cb *get_lbf_cb(const struct sk_buff *skb)
{
	qdisc_cb_private_validate(skb, sizeof(struct lbf_skb_cb));

	return (struct lbf_skb_cb *)qdisc_skb_cb(skb)->data;
}

static psched_time_t lbf_get_enqueue_time(const struct sk_buff *skb)
{
	return get_lbf_cb(skb)->enqueue_time;
}

static __u64 lbf_get_val(const struct sk_buff *skb){ 
	return get_lbf_cb(skb)->val;
}

static void lbf_set_enqueue_time(struct sk_buff *skb)
{
	get_lbf_cb(skb)->enqueue_time = psched_get_time();
}
__u16 lbf_get_min_delay(__u16 e_delay_new, __u16 min_delay, __u16 fib_todelay, __u16 fib_tohops)
{
	__u16 qmin = 0;
	if (min_delay > (e_delay_new + fib_todelay))  
		qmin = min_delay - (e_delay_new + fib_todelay);

	if (fib_tohops == 0)
	{
		printk("fib_to_hops is 0");
		return 0;
	}
	__u16 lqmin = qmin / fib_tohops;
	return lqmin;
}
__u16 lbf_get_max_delay(__u16 e_delay_new, __u16 max_delay, __u16 fib_todelay, __u16 fib_tohops)
{
	__u16 qmax = 0;
	if (max_delay > 0)
	{
		qmax = max_delay - (e_delay_new + fib_todelay);
	}
	if (fib_tohops == 0)
	{
		printk("fib_to_hops is 0");
		return 0;
	}
	__u16 lmax = (max_delay == 0) ? DMAX_BESTEFFORT : (qmax/ fib_tohops);
	return lmax;
}

static struct lbf_hnode *create_hnode(int lqbudget, int hnode_num)
{
    struct lbf_hnode *new_hnode;
    uint16_t mod;

    new_hnode = kcalloc(1, sizeof (struct lbf_hnode), GFP_KERNEL);
    if (new_hnode == NULL) {
        printk("hnode allocation failed\n");
        return (NULL);
    }
    mod = lqbudget % LQB_RANGE;
    new_hnode->range_start = lqbudget - mod;
    new_hnode->range_end = new_hnode->range_start + LQB_RANGE - 1;
	new_hnode->hnode_num = hnode_num;
	new_hnode->queue = NULL;
	new_hnode->next_hnode = NULL;
	new_hnode->prev_hnode = NULL;
    return new_hnode;
}

static inline void pnode_queue_add(struct lbf_hnode *hnode, struct sk_buff *realpkt, __u64 tmin_nsec, __u64 tmax_nsec, __u64 trcv_nsec)
{
	struct lbf_pnode *my_pnode, *prev_pnode, *curr_pnode;
	my_pnode = kcalloc(1, sizeof (struct lbf_pnode), GFP_KERNEL);
	if (my_pnode == NULL) 
	{
        printk("pnode allocation failed\n");
        return;
    }
	my_pnode->tmin_nsec = tmin_nsec;
    my_pnode->tmax_nsec = tmax_nsec;
    my_pnode->trcv      = trcv_nsec;
    my_pnode->realpkt = realpkt;
	my_pnode->next = NULL;
	my_pnode->hnode = NULL;
	printk("tmin_nsec from pnode %lld", my_pnode->tmin_nsec);
	if (hnode->queue == NULL)
	{
		my_pnode->hnode = hnode;
		hnode->queue = my_pnode;
	}	
	else 
	{
		struct lbf_pnode* pnode_queue = hnode->queue;
        prev_pnode = curr_pnode = pnode_queue;
        while (1) 
		{
            if (curr_pnode == NULL) 
			{
                prev_pnode->next = my_pnode;
                break;
            }
            if (tmin_nsec < curr_pnode->tmin_nsec)
			{
                if (prev_pnode == curr_pnode)
				{
					hnode->queue = my_pnode;
					curr_pnode->hnode = NULL;
					my_pnode->hnode = hnode;
				}
                else
				{
					prev_pnode->next = my_pnode;
				}
                    

                my_pnode->next = curr_pnode;
                break;
            }
            prev_pnode = curr_pnode;
            curr_pnode = curr_pnode->next;
        }
    }
	return;

}

static inline struct lbf_hnode* 
lbf_get_hnode (struct lbf_hnode_head ** list_ptr, int lqbudget)
{
	if (*list_ptr == NULL)
	{
		struct lbf_hnode_head* temp = kcalloc(1, sizeof (struct lbf_hnode), GFP_KERNEL);
		temp->head = NULL;
		temp->tail = NULL;
		temp->len = 0;
		*list_ptr = temp;
	}
	struct lbf_hnode *new_hnode, *curr_hnode, *prev_hnode;
	struct lbf_hnode_head* list = *list_ptr;
    curr_hnode = prev_hnode = list->head;
    if (curr_hnode == NULL) {
        new_hnode = create_hnode(lqbudget, list->len);
        if (!new_hnode)
            return NULL;
		list->len++;
        list->head = new_hnode;
        return new_hnode;
    }
    while (1) {
        if (curr_hnode == NULL) 
        {
            new_hnode = create_hnode(lqbudget, list->len);
            if (!new_hnode)
                return NULL;
            prev_hnode->next_hnode = new_hnode;
			list->len++;
            return new_hnode;
        }
        if ((lqbudget >= curr_hnode->range_start) &&
            (lqbudget < curr_hnode->range_end)) 
            {
                return curr_hnode;
            } 
        else if (lqbudget < curr_hnode->range_start) 
        {
            new_hnode = create_hnode(lqbudget, list->len);
            if (!new_hnode)
                return NULL;
            new_hnode->next_hnode = curr_hnode;
            if (curr_hnode == prev_hnode) 
            {
                list->head = new_hnode;
            } 
            else 
            {
                prev_hnode->next_hnode = new_hnode;
            }
			list->len++;
            return new_hnode;
        }
        prev_hnode = curr_hnode;
        curr_hnode = curr_hnode->next_hnode;
    }
	return NULL;
}

static int lbf_enqueue(struct sk_buff *skb, struct Qdisc *sch,
					   struct sk_buff **to_free)
{
	struct lbf_sched_data* q = qdisc_priv(sch);
	if (unlikely(qdisc_qlen(sch) >= sch->limit))
	{
		q->stats.overlimit++;
		return qdisc_drop(skb, sch, to_free);
	}
	lbf_set_enqueue_time(skb);
	// struct lbf_sched_data* q = qdisc_priv(sch);
	struct ethhdr *eth = (struct ethhdr *)skb_mac_header(skb);
	if (eth->h_proto == htons(ETH_P_NEWIP))
	{
		struct newip_offset *newipoff = (struct newip_offset *)skb_network_header(skb);
		printk("contract offset: %d",newipoff->contract_offset);
		if (newipoff->contract_offset != newipoff->payload_offset || newipoff->contract_offset != 0)
		{
			void *contract = skb_network_header(skb) + newipoff->contract_offset;
			if (*(__u16 *)contract == htons(1))
			{ //Max Delay Forwarding
				//Should be handled at dequeue
			}
			else if (*(__u16 *)contract == htons(2))
			{ //Latency Based Forwarding
				__u64 trcv   = lbf_get_val(skb);			//TODO use this for receving time

				struct lbf_sched_data* q = qdisc_priv(sch);
				
				struct latency_based_forwarding *lbf = (struct latency_based_forwarding*)contract;
				int ret = 0;
				// if (lbf->fib_tohops <= 0 || lbf->fib_todelay <= 0)
				if (lbf->fib_tohops <= 0)
				{
					printk("to_hops can not be zero, dropping the packet");
					ret = 1;
					qdisc_qstats_drop(sch);
					__qdisc_drop(skb, to_free);
					return ret;
				}

				__u16 h_delay = 0; //delay on this hop
				// Updating experienced delay 
				lbf->experienced_delay = htons(ntohs(lbf->experienced_delay) + h_delay*10); // calculating in 10^-4s so converting h_delay (ms) to 10^-4s
				lbf->fib_todelay = htons(ntohs(lbf->fib_todelay) - h_delay);

				__u16 e_delay_new = ntohs(lbf->experienced_delay); // stored in 10 ^-4s
				// calculating everthing in 10^ -4s
				__u16 min_delay = ntohs (lbf->min_delay) * 10;
				__u16 max_delay = ntohs (lbf->max_delay) * 10;
				__u16 fib_todelay = ntohs (lbf->fib_todelay) * 10;
				__u16 fib_tohops = ntohs (lbf->fib_tohops);
				// we can remove e_delay_new as thats lbf->experienced_delay now
				__u16 lqmin = lbf_get_min_delay(e_delay_new, min_delay, fib_todelay, fib_tohops); // in 10^-4s
				// printk("in enqueue lqmin %d",lqmin);
				__u16 lqmax = lbf_get_max_delay (e_delay_new, max_delay, fib_todelay, fib_tohops); // in 10^-4s
				// printk("lqmax in enqueue %d",lqmax);
				// printk("min_delay %d",min_delay);
				// printk("e_delay_new %d",ntohs(lbf->experienced_delay));
				// printk("fib_todelay %d",fib_todelay);
				// printk("fib_tohops %d",fib_tohops);

				lbf->fib_tohops = lbf->fib_tohops - htons(1);
				q->vars.hops_left = lbf->fib_tohops;
				int badpkt = 0;
				__u16 lqbudget = LQB_BESTEFFORT; 
				__u64 tmin_nsec, tmax_nsec;

				if (max_delay > 0)  
				{
					lqbudget = lqmax - lqmin;

					// early discard
					if ((e_delay_new + fib_todelay) > max_delay) {
						qdisc_qstats_drop(sch);
						printk( "%s(): iif early discard edelay %hu todelay %hu "
							"maxdelay %hu\n", __FUNCTION__,e_delay_new, 
							fib_todelay, max_delay); 
							return -1;
						badpkt++;
					}
				}

				__u64 curr_time = PSCHED_TICKS2NS(psched_get_time());

				tmin_nsec = curr_time + (__u64)lqmin * NSEC_PER_USEC * 100;
				tmax_nsec = curr_time + (__u64)lqmax * NSEC_PER_USEC * 100;

				/* 
				* tmax_nsec, tmin_nsec:
				*      Calculate absolute time range when we can send the packet
				* trcv: 
				*    Calculate absolute time at which oif_fn thinks the packet was received.
				*    This is then used to calculate how long the packet stayed in the
				*    the DBF queue.
				*/

				if (badpkt) 
				{
					printk("bad packet problem\n"); 
					return -1;
				}
				    

				struct lbf_hnode* hnode = lbf_get_hnode (&q->hnode_list, lqbudget);
				if (hnode == NULL) 
				{
					printk("Failed to find pifo head for %hu\n", lqbudget);
					return (1);
				}

				pnode_queue_add(hnode, skb, tmin_nsec, tmax_nsec, trcv);
				qdisc_qstats_backlog_inc(sch, skb);
				sch->q.qlen++;
				return NET_XMIT_SUCCESS;
			}
		}
	}
	return qdisc_enqueue_tail(skb, sch);
}



static inline void remove_pnode(struct lbf_pnode* pnode)
{
	
	if (pnode->next != NULL)
	{
		pnode->hnode->queue = pnode->next;
		pnode->next->hnode = pnode->hnode;
		
	}
	else
	{	// only pnode in hnode queue, need to remove hnode
		if(pnode->hnode->prev_hnode == NULL)
		{// Head Hnode
			// Lets just keep this hnode, we dont have access to hnode_head to change pointer
			pnode->hnode->queue = NULL;
		}
		else 
		{
			// we are in the middle or end of hnode queue
			pnode->hnode->prev_hnode->next_hnode = pnode->hnode->next_hnode;
			if (pnode->hnode->next_hnode != NULL)
			{
				pnode->hnode->next_hnode->prev_hnode = pnode->hnode->prev_hnode;
			}
			kfree(pnode->hnode);

		}
	}
	kfree(pnode);
}

static inline struct lbf_pnode* search_next_pnode(struct lbf_sched_data *q)
{
	__u64 curr_time = PSCHED_TICKS2NS(psched_get_time());

	__u64 tmin = ULLONG_MAX;
	struct lbf_pnode* ret = NULL;

	if (q->hnode_list!=NULL)
	{
		struct lbf_hnode* curr_hnode = q->hnode_list->head;
		struct lbf_pnode *curr_pnode = NULL;
		
		while (curr_hnode)
		{
			curr_pnode = curr_hnode->queue;

			while (curr_pnode)
			{	
				if (curr_pnode->tmax_nsec < curr_time && q->vars.hops_left == 0)
				{
					{	// Packet expired
						// Need to remove this node
						// we'll remove the hnode too if its not the head so go back to previous hnode but only if its not head hnode
						struct lbf_pnode* del_pnode = curr_pnode;
						printk("delayed by in search next  in 10^-4s: %lld",(curr_time-curr_pnode->tmax_nsec)/(NSEC_PER_MSEC/10));
						if (curr_pnode->next == NULL)
						{
							if (curr_hnode->prev_hnode != NULL)
							{
								curr_hnode = curr_hnode->prev_hnode;
							}
							curr_pnode = NULL;
						}
						else
						{
							curr_pnode = curr_pnode->next;
						}
						
						remove_pnode(del_pnode);
					}
					
				}
				else
				{
					if (curr_pnode->tmin_nsec < tmin)
					{
						tmin = curr_pnode->tmin_nsec;
						ret = curr_pnode;
					}

					curr_pnode = NULL;
				}
			}
			curr_hnode = curr_hnode->next_hnode;
		}
	}
	return ret;
}

static inline struct lbf_pnode* search_now_pnode(struct lbf_sched_data *q)
{
	__u64 curr_time = PSCHED_TICKS2NS(psched_get_time());
	bool hnode_updated = false;

	if (q->hnode_list!=NULL)
	{
		struct lbf_hnode* curr_hnode = q->hnode_list->head;
		struct lbf_pnode *curr_pnode = NULL;
		
		while (curr_hnode)
		{
			curr_pnode = curr_hnode->queue;

			while (curr_pnode)
			{	
				if (curr_pnode->tmin_nsec <= curr_time)
				{					
					if (curr_pnode->tmax_nsec < curr_time && q->vars.hops_left == 0)

					{	// Packet expired
						// Need to remove this node
						printk("delayed by in 10^-4s: %lld",(curr_time-curr_pnode->tmax_nsec)/(NSEC_PER_MSEC/10));
						struct lbf_pnode* del_pnode = curr_pnode;
						if (curr_pnode->next == NULL)
						{
							if (curr_hnode->prev_hnode != NULL)
							{
								curr_hnode = curr_hnode->prev_hnode;
							}
							curr_pnode = NULL;
						}
						else
						{
							curr_pnode = curr_pnode->next;
						}
						
						remove_pnode(del_pnode);
					}
					else 
					{
						// printk("Left time in 10^-4s %lld",(curr_pnode->tmax_nsec-curr_time)/(NSEC_PER_MSEC/10));
						// printk("found packet to be dequeued");
						return curr_pnode;
						// found packet to be dequeued
					}
				}
				else
				{
					// early packet. move to next hnode, end current pnode queue
					curr_pnode = NULL;
				}
				

			}
			curr_hnode = curr_hnode->next_hnode;
		}
	}
	return NULL;
}


static struct sk_buff *lbf_dequeue(struct Qdisc *sch)
{
	struct lbf_sched_data *q = qdisc_priv (sch);
	struct sk_buff *skb = NULL;
	struct lbf_pnode* next_pnode = NULL;
	__u64 curr_time = PSCHED_TICKS2NS(psched_get_time());

	if (q->next_pnode != NULL)
	{
		if (q->next_pnode->tmax_nsec > curr_time)
			printk("left time in 10^-4s: %lld",(q->next_pnode->tmax_nsec-curr_time)/(NSEC_PER_MSEC/10));
		else
			printk("late by in 10^-4s: %lld",(curr_time - q->next_pnode->tmax_nsec)/(NSEC_PER_MSEC/10));
		if (q->next_pnode->tmax_nsec < curr_time && q->vars.hops_left == 0)
		{
			printk("packet expired, maybe watchdog is late");
			qdisc_qstats_drop(sch);
			q->next_pnode->realpkt = NULL;
			remove_pnode (q->next_pnode);
			q->next_pnode = NULL;
		}
		else if (q->next_pnode->tmin_nsec > curr_time)
		{
			printk ("next_pnode is not ready to be sent yet");
		}
		else
		{
			skb = q->next_pnode->realpkt;
			q->next_pnode->realpkt = NULL;
			remove_pnode (q->next_pnode);
			q->next_pnode = NULL;
		}
		
	}

	struct lbf_pnode* pnode_now = search_now_pnode(q);
	if (pnode_now != NULL)
	{
		skb = pnode_now->realpkt;
		pnode_now->realpkt = NULL;
		remove_pnode(pnode_now);
	}
	
	next_pnode = search_next_pnode (q);
	
	if (next_pnode != NULL && next_pnode != q->next_pnode)
	{
		q->next_pnode = next_pnode;
		qdisc_watchdog_schedule_ns(&q->watchdog, q->next_pnode->tmin_nsec);
	}
	if (skb != NULL)
	{
		q->stats.delay = PSCHED_TICKS2NS(psched_get_time() - lbf_get_enqueue_time(skb))/NSEC_PER_USEC; // in usec
		// printk("Time stayed in queue: %lld",q->stats.delay/100);   // in 10^-4s
		struct newip_offset *newipoff = (struct newip_offset *)skb_network_header(skb);
		if (newipoff->contract_offset != newipoff->payload_offset || newipoff->contract_offset != 0)
		{
			void *contract = skb_network_header(skb) + newipoff->contract_offset;
			struct latency_based_forwarding *lbf = (struct latency_based_forwarding*)contract;
			lbf->experienced_delay = htons(ntohs(lbf->experienced_delay) + q->stats.delay/100); // in 10 ^-4s
			printk ("updated experienced delay %lld", ntohs(lbf->experienced_delay));
		}
	}


	if (likely(skb != NULL)) 
	{
		skb->next = NULL;
		qdisc_qstats_backlog_dec(sch, skb);
		qdisc_bstats_update(sch, skb);
		sch->q.qlen--;
		return skb;
	}


	skb = qdisc_dequeue_head(sch);
	if (unlikely(!skb))
		return NULL;

	q->stats.delay = psched_get_time() - lbf_get_enqueue_time(skb);

	struct ethhdr *eth = (struct ethhdr *)skb_mac_header(skb);
	if (eth->h_proto == htons(ETH_P_NEWIP))
	{
		struct newip_offset *newipoff = (struct newip_offset *)skb_network_header(skb);
		if (newipoff->contract_offset != newipoff->payload_offset || newipoff->contract_offset != 0)
		{
			struct max_delay_forwarding *mdf = (struct max_delay_forwarding *)(skb_network_header(skb) + newipoff->contract_offset);
			if (mdf->contract_type == htons(1))
			{ //Max Delay Forwarding
				__u16 max_allowed_delay = ntohs(mdf->max_allowed_delay);
				__u16 delay_exp = ntohs(mdf->delay_exp);

				// printk(KERN_INFO "delay: %lld %d %lld\n", delay_exp + q->stats.delay, delay_exp, q->stats.delay);
				if (delay_exp + q->stats.delay > max_allowed_delay)
				{
					/* Drop packet */
					kfree_skb(skb);
					qdisc_qstats_drop(sch);
					return NULL;
				}
				else
				{
					mdf->delay_exp = htons(delay_exp + q->stats.delay);
				}
			}
		}
	}

	return skb;
}

static struct sk_buff *lbf_peek(struct Qdisc *sch)
{
	return qdisc_peek_dequeued(sch);
}

static const struct nla_policy lbf_policy[TCA_LBF_MAX + 1] = {
	[TCA_LBF_LIMIT] = {.type = NLA_U32}};

static int lbf_change(struct Qdisc *sch, struct nlattr *opt,
					  struct netlink_ext_ack *extack)
{
	struct nlattr *tb[TCA_LBF_MAX + 1];
	int err;

	if (!opt)
		return -EINVAL;

	err = nla_parse_nested(tb, TCA_LBF_MAX, opt, lbf_policy, NULL);
	if (err < 0)
		return err;

	if (tb[TCA_LBF_LIMIT])
		sch->limit = nla_get_u32(tb[TCA_LBF_LIMIT]);

	return 0;
}

static int lbf_init(struct Qdisc *sch, struct nlattr *opt,
					struct netlink_ext_ack *extack)
{
	struct lbf_sched_data *q = qdisc_priv(sch);

	sch->limit = 1000;
	q->hnode_list = NULL;
	q->next_pnode = NULL;
	lbf_params_init(&q->params);
	lbf_vars_init(&q->vars);
	lbf_stats_init(&q->stats);
	qdisc_watchdog_init(&q->watchdog, sch);  // Uses CLOCK_MONOTONIC by default
	return lbf_change(sch, opt, extack);
}

static void lbf_reset(struct Qdisc *sch)
{
	struct lbf_sched_data *q = qdisc_priv (sch);
	if (q->watchdog.qdisc == sch)
		qdisc_watchdog_cancel(&q->watchdog);
	qdisc_reset_queue(sch);
}

static void lbf_destroy(struct Qdisc *sch)
{
	struct lbf_sched_data *q = qdisc_priv (sch);
	if (q->watchdog.qdisc == sch)
		qdisc_watchdog_cancel(&q->watchdog);
}

//static void lbf_attach(struct Qdisc *sch)
//{
//}

//static int lbf_change_tx_queue_len(struct Qdisc *sch, unsigned int new_len)
//{
//	return 0;
//}

static int lbf_dump(struct Qdisc *sch, struct sk_buff *skb)
{
	struct nlattr *opts;

	opts = nla_nest_start(skb, TCA_OPTIONS);
	if (unlikely(!opts))
		return -EMSGSIZE;

	if (nla_put_u32(skb, TCA_LBF_LIMIT, sch->limit))
		goto nla_put_failure;

	return nla_nest_end(skb, opts);

nla_put_failure:
	nla_nest_cancel(skb, opts);
	return -EMSGSIZE;
}

static int lbf_dump_stats(struct Qdisc *sch, struct gnet_dump *d)
{
	struct lbf_sched_data *q = qdisc_priv(sch);
	struct tc_lbf_xstats st = {
		.delay = q->stats.delay,
		.overlimit = q->stats.overlimit};

	return gnet_stats_copy_app(d, &st, sizeof(st));
}

//static void lbf_ingress_block_set(struct Qdisc *sch, u32 block_index)
//{
//}

//static void lbf_egress_block_set(struct Qdisc *sch, u32 block_index)
//{
//}

//static u32 lbf_ingress_block_get(struct Qdisc *sch)
//{
//	return U32_MIN;
//}

//static u32 lbf_egress_block_get(struct Qdisc *sch)
//{
//	return U32_MIN;
//}

static struct Qdisc_ops lbf_qdisc_ops __read_mostly = {
	.id = "lbf",
	.priv_size = sizeof(struct lbf_sched_data),
	//	.static_flags		= 0U,

	.enqueue = lbf_enqueue,
	.dequeue = lbf_dequeue,
	.peek = lbf_peek,

	.init = lbf_init,
	.reset = lbf_reset,
	.destroy = lbf_destroy,
	.change = lbf_change,
	//	.attach			= lbf_attach,
	//	.change_tx_queue_len	= lbf_change_tx_queue_len,

	.dump = lbf_dump,
	.dump_stats = lbf_dump_stats,

	//	.ingress_block_set	= lbf_ingress_block_set,
	//	.egress_block_set	= lbf_egress_block_set,
	//	.ingress_block_get	= lbf_ingress_block_get,
	//	.egress_block_get	= lbf_egress_block_get,

	.owner = THIS_MODULE};

static int __init lbf_module_init(void)
{
	printk("lbf init\n");
	return register_qdisc(&lbf_qdisc_ops);
}

static void __exit lbf_module_exit(void)
{
	printk("lbf exit\n");
	unregister_qdisc(&lbf_qdisc_ops);
}

module_init(lbf_module_init);
module_exit(lbf_module_exit);

MODULE_DESCRIPTION("Latency Based Forwarding queue discipline");
MODULE_AUTHOR("Bhaskar Kataria");
MODULE_AUTHOR("Rohit MP");
MODULE_LICENSE("GPL v2");
