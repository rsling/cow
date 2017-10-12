#!/bin/bash

set -e
set -u

source 	_opts.sh

sed -n 1,93510p ../tigercow.conll > split1.conll
sed -n 93510,191188p ../tigercow.conll > split2.conll
sed -n 191188,287098p ../tigercow.conll > split3.conll
sed -n 287098,383998p ../tigercow.conll > split4.conll
sed -n 383998,478456p ../tigercow.conll > split5.conll
sed -n 478456,573913p ../tigercow.conll > split6.conll
sed -n 573913,671333p ../tigercow.conll > split7.conll
sed -n 671333,758457p ../tigercow.conll > split8.conll
sed -n 758457,840680p ../tigercow.conll > split9.conll
sed -n 840680,938710p ../tigercow.conll > split10.conll
