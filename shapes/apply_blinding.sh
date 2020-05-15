#!/bin/bash

ERA=$1
CHANNEL=$2
TAG=$3
MODE=$4

source utils/setup_cvmfs_sft.sh
source utils/bashFunctionCollection.sh
if [[ $MODE == "global" ]]; then
    python shapes/apply_blinding.py output/shapes/${TAG}/${ERA}-${TAG}-${CHANNEL}-shapes.root \
        --threshold 0.49 --uncertainty 0.09 \
        --signal-processes ggH qqH VH WH ZH ttH \
        --exclude-categories _ss _B _sumW _sumEWKZ _FF \
        --global_blinding \
        --signal-categories ggh_0J ggh_1J_PTH0to120  ggh_2J qqh_2J xxh ggh qqh ggh_0J_PTH_0_10 ggh_0J_PTH_GT10 ggh_1J_PTH0to60 ggh_1J_PTH60to120 ggh_1J_PTH120to200 ggh_2J_PTH0to60 ggh_2J_PTH60to120 ggh_2J_PTH120to200 ggh_PTHGT200 qqh_2J qqh_PTHGT200 vbftopo_highmjj vbftopo_lowmjj qqh_vbftopo_highmjj qqh_vbftopo_lowmjj ggh_vbftopo ggh_PTH_200_300 ggh_PTHGT300

else
    logandrun python shapes/apply_blinding.py output/shapes/${TAG}/${ERA}-${TAG}-${CHANNEL}-shapes.root \
        --threshold 0.5 --uncertainty 0.09 \
        --signal-processes ggH qqH WH ZH ttH \
        --exclude-categories _ss _B _sumW _sumEWKZ _FF
fi 

