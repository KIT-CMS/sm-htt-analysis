#!/bin/bash

ERA=$1
CHANNEL=$2
TAG=$3
MODE=$4

source utils/setup_cvmfs_sft.sh
if [[ $MODE == "global" ]]; then
    python shapes/apply_blinding.py output/shapes/${TAG}/${ERA}-${TAG}-${CHANNEL}-shapes.root \
        --threshold 0.49 --uncertainty 0.09 \
        --signal-processes ggH qqH VH WH ZH ttH \
        --exclude-categories _ss _B _sumW _sumEWKZ _FF \
        --global_blinding \
        --signal-categories ggh_0J ggh_1J_PTH0to120 ggh_1J_PTH120to200 ggh_2J ggh_PTHGT200 qqh_2J qqh_PTHGT200 vbftopo_highmjj vbftopo_lowmjj xxh ggh qqh

else
    python shapes/apply_blinding.py output/shapes/${TAG}/${ERA}-${TAG}-${CHANNEL}-shapes.root \
        --threshold 0.5 --uncertainty 0.09 \
        --signal-processes ggH qqH VH \
        --exclude-categories _ss _B _sumW _sumEWKZ _FF
fi