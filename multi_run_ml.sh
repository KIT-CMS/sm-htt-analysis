#!/bin/bash

#This script starts multiple runs with the given settings using the run_ml_condor.sh script

ERAS="all_eras"
#Can be: all_eras 2016 2017 2018
CHANNELS="tt"
#Can be: et mt tt
MASSES="550"
#Can be: 240 280 320 360 400 450 500 550 600 700 800 900 1000 1200
BATCHES="1"
#Can be: 1 2 3 4 5 6 7
#Use `python ml/get_nBatches.py ${MASS}` when also iterating over masses

OPTIONS="2p"
#One series of runs is started per set of options
#Possible options (order doesn't matter):
#1 - Remake the training data
#2 - Retrain the modell
#3 - Test the modells again
#c - use CPU instead of GPU to train modells
#p - run all runs parallel
#n - don't wait for subprocesses after run

#Loop for multiple sets of runs
for OPTION in ${OPTIONS}; do
  #Loop for different Eras
  for ERA in ${ERAS}; do
    #Loop for different Channels
    for CHANNEL in ${CHANNELS}; do
      #Loop for different Masses
      for MASS in ${MASSES}; do
        #Loop for different Batches
        for BATCH in ${BATCHES}; do
          #Decide if runs are parallel and start runs with training on condor
          if [[ ${OPTION} == *"p"* ]]; then
            ./run_ml_condor.sh ${ERA} ${CHANNEL} ${MASS} ${BATCH} ${OPTION} &
          else
            ./run_ml_condor.sh ${ERA} ${CHANNEL} ${MASS} ${BATCH} ${OPTIONS}
          fi
        done
      done
    done
  done
  #Wait for all runs in set if not otherwise specified
  if [[ ! ${OPTION} == *"n"* ]]; then
    wait
  fi
done
wait
