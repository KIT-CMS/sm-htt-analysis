#!/bin/bash

source utils/setup_cmssw.sh

combine -M MaxLikelihoodFit --robustFit 1 -m 125 datacard.txt

