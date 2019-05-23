#!/bin/bash

ERA=$1

source utils/setup_cvmfs_sft.sh

PROCESSES="ggh qqh ztt tt ss misc db"
CHANNEL=em
for FOLD in 0 1
do
    python ./ml/sum_training_weights.py ml/${ERA}_${CHANNEL}/fold${FOLD}_training_dataset.root $PROCESSES
    echo
done

hadd -f ml/${ERA}_${CHANNEL}/combined_training_dataset.root \
    ml/${ERA}_${CHANNEL}/fold0_training_dataset.root \
    ml/${ERA}_${CHANNEL}/fold1_training_dataset.root
echo
python ./ml/sum_training_weights.py ml/${ERA}_${CHANNEL}/combined_training_dataset.root $PROCESSES
echo

PROCESSES="ggh qqh ztt noniso misc"
CHANNEL=tt
for FOLD in 0 1
do
    python ./ml/sum_training_weights.py ml/${ERA}_${CHANNEL}/fold${FOLD}_training_dataset.root $PROCESSES
    echo
done

hadd -f ml/${ERA}_${CHANNEL}/combined_training_dataset.root \
    ml/${ERA}_${CHANNEL}/fold0_training_dataset.root \
    ml/${ERA}_${CHANNEL}/fold1_training_dataset.root
echo
python ./ml/sum_training_weights.py ml/${ERA}_${CHANNEL}/combined_training_dataset.root $PROCESSES
echo

PROCESSES="ggh qqh ztt zll w tt ss misc"
CHANNEL=et
for FOLD in 0 1
do
    python ./ml/sum_training_weights.py ml/${ERA}_${CHANNEL}/fold${FOLD}_training_dataset.root $PROCESSES
    echo
done

hadd -f ml/${ERA}_${CHANNEL}/combined_training_dataset.root \
    ml/${ERA}_${CHANNEL}/fold0_training_dataset.root \
    ml/${ERA}_${CHANNEL}/fold1_training_dataset.root
echo
python ./ml/sum_training_weights.py ml/${ERA}_${CHANNEL}/combined_training_dataset.root $PROCESSES
echo

CHANNEL=mt
for FOLD in 0 1
do
    python ./ml/sum_training_weights.py ml/${ERA}_${CHANNEL}/fold${FOLD}_training_dataset.root $PROCESSES
    echo
done

hadd -f ml/${ERA}_${CHANNEL}/combined_training_dataset.root \
    ml/${ERA}_${CHANNEL}/fold0_training_dataset.root \
    ml/${ERA}_${CHANNEL}/fold1_training_dataset.root
echo
python ./ml/sum_training_weights.py ml/${ERA}_${CHANNEL}/combined_training_dataset.root $PROCESSES
echo
