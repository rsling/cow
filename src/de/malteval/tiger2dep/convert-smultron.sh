#!/bin/bash

# Usage: ./convert-smultron.sh smultron_de_alpine.xml smultron_de_dvdman.xml smultron_de_economy.xml smultron_de_sophie.xml

ALPINE=$1
ALPINEBASE=`basename $ALPINE`
DVDMAN=$2
DVDMANBASE=`basename $DVDMAN`
ECONOMY=$3
ECONOMYBASE=`basename $ECONOMY`
SOPHIE=$4
SOPHIEBASE=`basename $SOPHIE`

echo $ALPINE
python apply-corrections.py utf8 $ALPINE corrections/corrections-alpine.pl > $ALPINEBASE.corrected
python tigerxml2conll09.py -m corrections/manual_heads_alpine.pl -i $ALPINEBASE.corrected -d smultron > $ALPINEBASE.conll09

echo $DVDMAN
python apply-corrections.py utf8 $DVDMAN corrections/corrections-dvdman.pl > $DVDMANBASE.corrected
python tigerxml2conll09.py -m corrections/manual_heads_dvdman.pl -i $DVDMANBASE.corrected -d smultron > $DVDMANBASE.conll09

echo $ECONOMY
python apply-corrections.py utf8 $ECONOMY corrections/corrections-economy.pl > $ECONOMYBASE.corrected
python tigerxml2conll09.py -m corrections/manual_heads_economy.pl -i $ECONOMYBASE.corrected -d smultron > $ECONOMYBASE.conll09

echo $SOPHIE
python apply-corrections.py utf8 $SOPHIE corrections/corrections-sophie.pl > $SOPHIEBASE.corrected
python tigerxml2conll09.py -m corrections/manual_heads_sophie.pl -i $SOPHIEBASE.corrected -d smultron > $SOPHIEBASE.conll09
