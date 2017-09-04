#!/bin/bash

set -e
set -u

leadin='<?xml version="1.0" encoding="utf-8"?>\n<corpus>'
leadout='</corpus>'

echo "Checking ${1}..."
cat <(echo -e ${leadin}) <(gunzip -c ${1}) <(echo -e ${leadout}) | xmlwf -r

