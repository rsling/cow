#!/bin/bash

set -e
set -u

source 	_opts.sh

for s in ${EXPS[@]}
do
    echo
    echo "Applying for experiment $s"
    parallel --gnu --xapply "$MALT -c {1.} -i {2} -o $s{2.}ed.conll -m parse " ::: nivreeager01fold*train.mco ::: fold*test.conll
done
