#!/bin/bash

echo
echo "========================================================================"
echo "  You are only allowed to download TiGer after accepting the license"
echo "  agreement. Go to http://bit.ly/2gdTFi3 to accept it or abort."
echo "========================================================================"
echo
read -n1 -rsp $'Press any key to continue or Ctrl+C to exit...\n'

\rm -f tigercorpus*
wget http://www.ims.uni-stuttgart.de/forschung/ressourcen/korpora/TIGERCorpus/download/tigercorpus-2.2.xml.tar.gz
tar xvf tigercorpus-2.2.xml.tar.gz
\rm tigercorpus-2.2.xml.tar.gz
