#!/bin/bash

#ERA=$1
STXS_FIT=stxs_stage0
STXS_SIGNALS=stxs_stage0
era=$1
channel=$2
tag=$3

DATACARDDIR=output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}/$channel/125
FITFILE=$DATACARDDIR/fitDiagnostics.hesse-${era}-${tag}-${channel}-${STXS_FIT}.MultiDimFit.mH125.root

source utils/setup_cmssw.sh

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited

#echo ${era} $STXS_FIT $DATACARDDIR $channel ${tag} "robustHesse"
#exit

#./combine/signal_strength.sh ${ERA} "robustHesse"
./combine/signal_strength.sh ${era} $STXS_FIT $DATACARDDIR $channel ${tag} "robustHesse"

#python combine/plot_poi_correlation_final-stage-1p1.py ${ERA}_${STXS_FIT} fitDiagnostics${ERA}.root
python combine/plot_poi_correlation_final-stage-0.py ${ERA}_${STXS_FIT} $FITFILE
