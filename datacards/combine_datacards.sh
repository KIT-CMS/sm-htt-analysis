#!/bin/bash
set -e
IFS=',' read -r -a ERAS <<< $1
CHANNEL=$2
TAG=$3
STXS_SIGNALS=$4

set -x

TARGET=output/datacards/all-${TAG}-smhtt-ML/${STXS_SIGNALS}/$CHANNEL
## remove old files
ls $TARGET/125/htt_*_Run*.txt &> /dev/null && rm $TARGET/125/htt_*_Run*.txt
[[ -f $TARGET/common/htt_input_Run*.root ]] && rm $TARGET/common/htt_input_Run*.root
for ERA in ${ERAS[@]}; do
    DATACARDDIR=output/datacards/${ERA}-${TAG}-smhtt-ML/${STXS_SIGNALS}/$CHANNEL
    # Make new directory with needed folder structure
    mkdir -p $TARGET/{125,common}
    cp ${DATACARDDIR}/125/htt_*_Run${ERA}.txt $TARGET/125
    cp ${DATACARDDIR}/common/htt_input_Run${ERA}.root $TARGET/common
done
