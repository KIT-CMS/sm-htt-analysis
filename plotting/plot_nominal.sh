#!/bin/bash

source utils/setup_cmssw.sh

TRAINING=$1

./plotting/plot_nominal.py -v mt_${TRAINING}_max_score -c mt_ZTT mt_ZLL mt_W mt_TT mt_QCD --scale-signal 50
