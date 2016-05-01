#!/bin/bash

set -e
set -u

source 	_opts.sh

for i in $(seq 1 10)
do
    # Write test file.
   cat "split$i.conll" | sed '1{;/^$/d;}' > "fold$i""test.conll"

    # Get ranges for train file.
    l=`echo "$i-1" | bc`
    h=`echo "$i+1" | bc`

    # Write train file.
    tf="fold$i""train.conll"
    rm -f $tf
    for j in $(seq 1 $l)
    do
	echo -n "$j "
	cat "split$j.conll" >> $tf
    done

    echo -n " ! "

    for j in $(seq $h 10)
    do
	echo -n "$j "
	cat "split$j.conll" >> $tf
    done

    echo
done
