#!/bin/bash
########################################################
## Statistics generation script for MicroFaaS Project ##
## Boston University PEACLAB 2021                     ##
########################################################

# Bash script for parsing through multiple files to generate statistics for MicroFaaS run. 
# Usage: bash data_stats.sh [-e energy data] [FOLDER_CONTAINING_LOGS]
# exclude -e for microfaas logs
# Requires csv_data.py in working directory

if [ $1 == '-e' ]; then 
FILES=$2/*.csv 
for f in $FILES
do
	python3 energy_csv_data.py $f
done
else 

FILES=$1/*.log
for f in $FILES
do
	python3 csv_data.py $f
done	
fi