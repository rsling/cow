#!/bin/bash

# Pass: infile, outdir+prefix

#SBATCH --mem=16M
#SBATCH --time=06:00:00

set -e
set -u

cowsplit -i ${1} -o ${2} -r '^<doc ' -s 2500000
gzip "${2}*"
#cowsplit -i ${1} -o ${2} -r '^<doc ' -s 225000000
