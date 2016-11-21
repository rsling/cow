#!/bin/bash

# USAGE: ./convert-tiger.sh tiger_release_aug07.xml

TIGERXML=$1
BASENAME=`basename $TIGERXML`

# correct tiger version 2.1
python apply-corrections.py latin1 $TIGERXML corrections/corrections-tiger.pl > $BASENAME.corrected

# convert corrected version to dependencies
python tigerxml2conll09.py -m corrections/manual_heads_tiger.pl -i $BASENAME.corrected -d tiger > $BASENAME.conll09

