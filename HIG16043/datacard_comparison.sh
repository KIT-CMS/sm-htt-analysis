#!/bin/bash

DATACARD_1=$1
DATACARD_2=$2

source utils/setup_cvmfs_sft.sh

for PROCESS in "ZTT" "W" "ZJ" "ZL" "EWK" "EWKZ" "VV" "TTT" "TTJ" "QCD" "ggH125" "ggH_htt125" "qqH125" "qqH_htt125"
do
    python datacards/inspect_shapes.py -f $DATACARD_1 $DATACARD_2 -p $PROCESS
done
