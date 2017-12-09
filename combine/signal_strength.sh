#!/bin/bash

source utils/setup_cmssw.sh

combine -M MaxLikelihoodFit -m 125 datacard.txt --robustFit 1
