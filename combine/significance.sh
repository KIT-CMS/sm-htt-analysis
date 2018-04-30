#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

combine -M ProfileLikelihood -t -1 --expectSignal 1 --toysFrequentist --significance -m 125 -n $ERA ${ERA}_datacard.txt
