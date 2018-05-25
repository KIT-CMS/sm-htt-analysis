#!/bin/bash

ERA=$1

source utils/setup_cvmfs_sft.sh

PROCESSES="ggh qqh ztt noniso misc"
CHANNEL=tt
for FOLD in 0 1
do
    python ./ml/sum_training_weights.py ml/${ERA}_${CHANNEL}/fold${FOLD}_training_dataset.root $PROCESSES
    echo
done

PROCESSES="ggh qqh ztt zll w tt ss misc"
CHANNEL=et
for FOLD in 0 1
do
    python ./ml/sum_training_weights.py ml/${ERA}_${CHANNEL}/fold${FOLD}_training_dataset.root $PROCESSES
    echo
done

CHANNEL=mt
for FOLD in 0 1
do
    python ./ml/sum_training_weights.py ml/${ERA}_${CHANNEL}/fold${FOLD}_training_dataset.root $PROCESSES
    echo
done
