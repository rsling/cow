#!/bin/bash

# USAGE: ./convert-europarl.sh german_goldgold.xml

EUROPARL=$1
BASENAME=`basename $EUROPARL`

# correct tiger version 2.1
python apply-corrections.py utf8 $EUROPARL corrections/corrections-europarl.pl > $BASENAME.corrected

# convert corrected version to dependencies
python tigerxml2conll09.py -m corrections/manual_heads_europarl.pl -i $BASENAME.corrected -d europarl > $BASENAME.conll09

