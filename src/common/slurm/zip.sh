#!/bin/bash

# Pass: directory with files

#SBATCH --mem=16M
#SBATCH --time=03:00:00

set -e
set -u

gzip ${1}/*
