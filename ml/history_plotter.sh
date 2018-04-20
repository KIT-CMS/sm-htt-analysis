#!/bin/bash

CHANNEL=$1

source utils/setup_cvmfs_sft.sh

if [[ -d ml/${CHANNEL} ]]; then
  python ml/history_plotter.py ml/${CHANNEL}_training_config.yaml 0
  python ml/history_plotter.py ml/${CHANNEL}_training_config.yaml 1
fi

