#!/bin/bash

echo
echo "========================================================================"
echo "  The license for this data set is unknown to COW."
echo "  Please check whether you are allowed to use it before continuing."
echo "========================================================================"
echo
read -n1 -rsp $'Press any key to continue or Ctrl+C to exit...\n'

\rm -f german_goldgold* 
wget http://www.nlpado.de/~sebastian/data/projection/german_goldgold.xml.gz
gunzip german_goldgold.xml.gz
cd ../tiger2dep
\rm -f german_goldgold*
./convert-europarl707.sh ../europarl/german_goldgold.xml &> /dev/null
