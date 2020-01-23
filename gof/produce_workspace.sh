#!/bin/bash
set -e
source utils/setup_cmssw.sh
source utils/setup_python.sh

[[ ! -z $1 ]] || (echo Invalid number of arguments; exit 1  )
ERA=$1


LOGFILE=output/log/workspace-${ERA}.log

# Collect input directories for eras and define output path for workspace
INPUT=output/${ERA}_smhtt/cmb/125
echo "[INFO] Add datacards to workspace from path "${INPUT}"."

#OUTPUT=${ERA}_workspace.root
OUTPUT=${PWD}/${ERA}_workspace.root
echo "[INFO] Write workspace to "${OUTPUT}"."

# Clean previous workspace
rm -f $OUTPUT

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited

# Define signals to be fitted and produce workspace
combineTool.py -M T2W -o ${OUTPUT} -i ${INPUT} | tee $LOGFILE
