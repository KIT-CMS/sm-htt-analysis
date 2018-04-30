#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

combine -M MaxLikelihoodFit -m 125 ${ERA}_datacard.txt --robustFit 1 -n $ERA
