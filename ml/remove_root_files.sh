#!/bin/bash

ERA=$1 # Can be 2016, 2017, 2018 or "all"
CHANNEL=$2 # Can be et, mt or tt
MASS=$3 # only train on mH=500 GeV
BATCH=$4 # only train on mh' in 85, 90, 95, 100 GeV (see ml/get_nBatches.py for assignment)

if [[ ${_CONDOR_JOB_IWD} == "/var/lib/condor/execute/dir"* ]]; then
    echo "Removing .root files from output/ml/${ERA}_${CHANNEL}_${MASS}_${BATCH}"
    rm -r ${ERA}_${CHANNEL}_${MASS}_${BATCH}/*.root
else
    "Not running on HTCondor. Space should not be a problem."
fi
