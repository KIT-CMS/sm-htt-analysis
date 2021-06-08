#!/bin/bash
set -e
#This script starts multiple runs with the given settings using the run_ml_condor.sh script

ERAS="all_eras"
#Can be: all_eras 2016 2017 2018
CHANNELS="et" #et mt"
#Can be: et mt tt
MASSES="320 360 400 450 500 550 600 700"
#Can be: 240 280 320 360 400 450 500 550 600 700 800 900 1000 1200
BATCHES="4"
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
          ARGS_POOL+=("${ERA} ${CHANNEL} ${MASS} ${BATCH} GET_REMOTE")
        fi
      done
    done
  done
done
printf "%q\n" "${ARGS_POOL[@]}"
#Run ./run_ml.sh with args from ARGS_POOL. Maximum max-procs can run at once
printf "%q\n" "${ARGS_POOL[@]}"  | xargs --max-procs=8 -l bash -c './run_ml.sh $0 $1 $2 $3 $4'

