#!/bin/bash

CHANNEL=$1

source utils/setup_cvmfs_sft.sh

python ml/discretize_training_dataset.py gof/binning.yaml $CHANNEL ml/${CHANNEL}/fold0_${CHANNEL}_training_dataset.root tmp_${CHANNEL}.root --modify-num-bins 16
cp tmp_${CHANNEL}.root ml/${CHANNEL}/fold0_${CHANNEL}_training_dataset.root

python ml/discretize_training_dataset.py gof/binning.yaml $CHANNEL ml/${CHANNEL}/fold1_${CHANNEL}_training_dataset.root tmp_${CHANNEL}.root --modify-num-bins 16
cp tmp_${CHANNEL}.root ml/${CHANNEL}/fold1_${CHANNEL}_training_dataset.root

rm tmp_${CHANNEL}.root
