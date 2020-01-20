#!/bin/bash
set -e
IFS=',' read -r -a ERAS <<< $1
IFS=',' read -r -a CHANNELS <<< $2
TAG=$3
STXS_FIT=$4
# Clean any existing files
if [[ $STXS_FIT == "inclusive" || $STXS_FIT == "stxs_stage0" ]]; then
    STXS_SIGNALS=stxs_stage0
elif [[ $STXS_FIT == "stxs_stage1p1" ]] ; then
    STXS_SIGNALS=stxs_stage1p1
fi


for ERA in ${ERAS[@]}; do
    for CHANNEL in ${CHANNELS[@]}; do
        for STXS_SIGNALS in "stxs_stage0" "stxs_stage1p1"; do
            DATACARDDIR=output/datacards/${ERA}-${TAG}-smhtt-ML/${STXS_SIGNALS}/$CHANNEL
            TARGET=output/datacards/all-comberas-smhtt-ML/${STXS_SIGNALS}/$CHANNEL
            [[ -d $TARGET ]] && rm -r $TARGET
            # Make new directory with needed folder structure
            mkdir -p $TARGET/{125,common}

            cp ${DATACARDDIR}/125/htt_*_Run${ERA}.txt $TARGET/125
            cp ${DATACARDDIR}/common/htt_input_Run${ERA}.root $TARGET/common
        done
    done
done