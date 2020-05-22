#!/bin/bash
set -e
source utils/setup_cmssw.sh
source utils/setup_python.sh

[[ ! -z $1 && ! -z $2 && ! -z $3 ]] || (echo Invalid number of arguments; exit 1  )
ERA=$1
CHANNEL=$2
VARIABLE=$3


LOGFILE=output/log/workspace-${ERA}-${CHANNEL}-${VARIABLE}.log

# Collect input directories for eras and define output path for workspace
INPUT="output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-smhtt-gof/cmb/125"
echo "[INFO] Add datacards to workspace from path "${INPUT}"."

#OUTPUT=${ERA}_workspace.root
OUTPUT=${PWD}/output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-smhtt-gof/${ERA}-${CHANNEL}-${VARIABLE}-workspace.root
echo "[INFO] Write workspace to "${OUTPUT}"."

# Clean previous workspace
rm -f $OUTPUT

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited

# Define signals to be fitted and produce workspace
combineTool.py -M T2W -o ${OUTPUT} -i ${INPUT} --channel-masks | tee $LOGFILE
