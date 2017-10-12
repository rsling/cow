#!/bin/bash

#SBATCH --mem=31G

set -e
set -u

export PYTHONPATH=${HOME}/usr/local/lib64/python2.6/site-packages/
export MANATEE_REGISTRY=/scratch/rsling/encow16/13noske/registry

gunzip -c /scratch/rsling/encow16/11slices/encow16a??.xml.gz |
  sed '/^<doc / { s/last-modified/last_modified/ }' |
  sed '/^<doc / { s/_unk_/unknown/g }' |
  sed 's/&gt;/>/g' |
  sed 's/&lt;/</g' |
  sed 's/&quot;/"/g' |
  sed "s/&apos;/'/g" |
  sed 's/&amp;/\&/g' |
  grep -v '^<dup\|<\/dup\|^dupblank' |
  sed '/^<title>/,/^<\/title>/d' |
  sed '/^<keywords>/,/^<\/keywords>/d' |
  grep -v '^<meta ' | 
  cut -f1,2,3,4,6,11,12,13,14 |
  compilecorp --no-ske encow16a
