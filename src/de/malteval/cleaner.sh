#!/bin/bash

set -e
set -u

source 	_opts.sh

rm -f *fold*tested.conll
rm -f *fold*train.mco
rm -f split*.conll
rm -rf *fold*train/
