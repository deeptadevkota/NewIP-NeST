#!/bin/bash
# Runs the ss command

INTERVAL=0.002

dev="$1"
duration="$2"

command="tc -s -j qdisc show dev $dev"

# Runs the tc command for `duration`s every `INTERVAL`s
# Output of each tc iteration is separated by `---`
for i in $(seq 1 $INTERVAL $duration); do
	echo "timestamp:$(date +%s.%N)"
	eval $command
	if [ $? -ne 0 ]; then
		exit 1
	fi
	echo "---"
	sleep $INTERVAL
done