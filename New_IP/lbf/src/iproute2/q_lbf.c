// SPDX-License-Identifier: GPL-2.0-only

#include <stdio.h>
#include <string.h>

#include "utils.h"
#include "tc_util.h"

static void explain(void)
{
	fprintf(stderr,
		"Usage: ... lbf [ limit PACKETS ]\n");
}

static int lbf_parse_opt(struct qdisc_util *qu, int argc, char **argv,
			 struct nlmsghdr *n, const char *dev)
{
	unsigned int limit = 0;
	struct rtattr *tail;

	while (argc > 0) {
		if (strcmp(*argv, "limit") == 0) {
			NEXT_ARG();
			if (get_unsigned(&limit, *argv, 0)) {
				fprintf(stderr, "Illegal \"limit\"\n");
				return -1;
			}
		} else {
			fprintf(stderr, "What is \"%s\"?\n", *argv);
			explain();
			return -1;
		}

		argc--;
		argv++;
	}

	tail = addattr_nest(n, 1024, TCA_OPTIONS | NLA_F_NESTED);
	if (limit)
		addattr_l(n, 1024, TCA_LBF_LIMIT, &limit, sizeof(limit));
	addattr_nest_end(n, tail);

	return 0;
}

static int lbf_print_opt(struct qdisc_util *qu, FILE *f, struct rtattr *opt)
{
	struct rtattr *tb[TCA_LBF_MAX + 1];
	unsigned int limit;

	if (opt == NULL)
		return 0;

	parse_rtattr_nested(tb, TCA_LBF_MAX, opt);

	if (tb[TCA_LBF_LIMIT] &&
	    RTA_PAYLOAD(tb[TCA_LBF_LIMIT]) >= sizeof(__u32)) {
		limit = rta_getattr_u32(tb[TCA_LBF_LIMIT]);
		print_uint(PRINT_ANY, "limit", "limit %up ", limit);
	}

	return 0;
}

static int lbf_print_xstats(struct qdisc_util *qu, FILE *f,
			    struct rtattr *xstats)
{
	struct tc_lbf_xstats _st = {}, *st;

	SPRINT_BUF(b1);

	if (xstats == NULL)
		return 0;

	st = RTA_DATA(xstats);
	if (RTA_PAYLOAD(xstats) < sizeof(*st)) {
		memcpy(&_st, st, RTA_PAYLOAD(xstats));
		st = &_st;
	}

	print_uint(PRINT_JSON, "delay", NULL, st->delay);
	print_string(PRINT_FP, NULL, "  delay %s ", sprint_time(st->delay, b1));
	print_uint(PRINT_JSON, "overlimit", NULL, st->overlimit);
	// print_uint(PRINT_ANY, " delay", "delay %u ", st->delay);
	print_uint(PRINT_ANY, " overlimit", "overlimit %up", st->overlimit);
	// print_string(PRINT_FP, NULL, "  overlimit %s", sprint_size(st->overlimit, b1));

	return 0;
}

struct qdisc_util lbf_qdisc_util = {
	.id		= "lbf",
	.parse_qopt	= lbf_parse_opt,
	.print_qopt	= lbf_print_opt,
	.print_xstats	= lbf_print_xstats
};
