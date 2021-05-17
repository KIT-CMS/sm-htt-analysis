#!/bin/bash
set -e
#This script starts multiple runs with the given settings using the run_ml_condor.sh script

ERAS="2016"
#Can be: all_eras 2016 2017 2018
CHANNELS="tt" #et mt"
#Can be: et mt tt
MASSES="500"
#Can be: 240 280 320 360 400 450 500 550 600 700 800 900 1000 1200
BATCHES="2"
#Can be: 1 2 3 4 5 6 7
#Use `python ml/get_nBatches.py ${MASS}` when also iterating over masses

#Loop for different Eras
for ERA in ${ERAS}; do
  #Loop for different Channels
  for CHANNEL in ${CHANNELS}; do
    #Loop for different Masses
    for MASS in ${MASSES}; do
      # Check which batches are allowed for mass
      ALLOWED_BATCHES=`python ml/get_nBatches.py ${MASS}`
      #Loop for different Batches
      for BATCH in ${BATCHES}; do
        #Check if batch is possible for mass
        if [[ " ${ALLOWED_BATCHES[@]} " =~ " ${BATCH} " ]]; then
        custom_condor_scripts/custom_condor_run.sh "run_ml.sh ${ERA} ${CHANNEL} ${MASS} ${BATCH} GET_REMOTE" \
          -i output/log/logandrun/ htt-ml/ utils/ ml/ \
          -o output/ml/${ERA}_${CHANNEL}_${MASS}_${BATCH}/'*.!(root)' \
          -s custom_condor_scripts/custom_condor_default_submission.jdl \
          -q -t &
        fi
      done
    done
  done
done
wait