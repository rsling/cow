#!/bin/bash

set -e
set -u

source 	_opts.sh

for s in ${EXPS[@]}
do
    echo
    echo "Training for experiment $s"
    CONF="$s.xml"
    parallel --gnu "$MALT -f $CONF -i {} -c $s{.} -m learn" ::: fold*train.conll
done

