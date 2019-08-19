#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

[[ ! -z $1 && ! -z $2 && ! -z $3 ]] || (echo Invalid number of arguments; exit 1  )
ERA=$1
STXS_FIT=$2
TRAINING_METHOD=$3
NUM_THREADS=12

if [[ $STXS_FIT == "inclusive" || $STXS_FIT == "stxs_stage0" ]]; then
    STXS_SIGNALS=stxs_stage0
elif [[ $STXS_FIT == "stxs_stage1p1" ]] ; then
    STXS_SIGNALS=stxs_stage1p1
fi

LOGFILE=output/log/workspace-${ERA}-$STXS_FIT-${TRAINING_METHOD}.log

# Collect input directories for eras and define output path for workspace
INPUT=output/datacards/${ERA}-${TRAINING_METHOD}-smhtt-ML/${STXS_SIGNALS}/*/125
echo "[INFO] Add datacards to workspace from path "${INPUT}"."

OUTPUT=${ERA}-${STXS_FIT}-workspace.root
#OUTPUT=${PWD}/${ERA}_workspace.root
echo "[INFO] Write workspace to "${OUTPUT}"."

# Clean previous workspace
rm -f $OUTPUT

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited

# Define signals to be fitted and produce workspace
if [ $STXS_FIT == "inclusive" ]; then
    combineTool.py -M T2W -o ${OUTPUT} -i ${INPUT} --parallel $NUM_THREADS | tee $LOGFILE
fi
if [ $STXS_FIT == "stxs_stage0" ]; then
    combineTool.py -M T2W -o ${OUTPUT} -i ${INPUT} --parallel $NUM_THREADS \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=^.*/ggH.?$:r_ggH[1,-5,5]"' \
        --PO '"map=^.*/qqH.?$:r_qqH[1,-5,5]"' | tee $LOGFILE
fi

# Stage 1.1 as unified for the MC production, see https://indico.cern.ch/event/820874/contributions/3431583/attachments/1843868/3024330/Legacy_SM_H_-_Status.pdf, Slide 4
if [ $STXS_FIT == "stxs_stage1p1" ]; then
    combineTool.py -M T2W -o ${OUTPUT} -i ${INPUT} --parallel $NUM_THREADS \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=^.*/ggH_GG2H_FWDH:r_ggH_GG2H_0J[1,-70,70]"' \
        --PO '"map=^.*/ggH_GG2H_PTH_GT200:r_ggH_GG2H_PTH_GT200[1,-70,70]"' \
        --PO '"map=^.*/ggH_GG2H_0J_PTH_0_10:r_ggH_GG2H_0J[1,-70,70]"' \
        --PO '"map=^.*/ggH_GG2H_0J_PTH_GT10:r_ggH_GG2H_0J[1,-70,70]"' \
        --PO '"map=^.*/ggH_GG2H_1J_PTH_0_60:r_ggH_GG2H_1J_PTH_0_120[1,-70,70]"' \
        --PO '"map=^.*/ggH_GG2H_1J_PTH_60_120:r_ggH_GG2H_1J_PTH_0_120[1,-70,70]"' \
        --PO '"map=^.*/ggH_GG2H_1J_PTH_120_200:r_ggH_GG2H_1J_PTH_120_200[1,-70,70]"' \
        --PO '"map=^.*/ggH_GG2H_GE2J_MJJ_0_350_PTH_0_60:r_ggH_GG2H_GE2J_PTH_0_200[1,-70,70]"' \
        --PO '"map=^.*/ggH_GG2H_GE2J_MJJ_0_350_PTH_60_120:r_ggH_GG2H_GE2J_PTH_0_200[1,-70,70]"' \
        --PO '"map=^.*/ggH_GG2H_GE2J_MJJ_0_350_PTH_120_200:r_ggH_GG2H_GE2J_PTH_0_200[1,-70,70]"' \
        --PO '"map=^.*/ggH_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25:r_ggH_GG2H_GE2J_PTH_0_200[1,-70,70]"' \
        --PO '"map=^.*/ggH_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25:r_ggH_GG2H_GE2J_PTH_0_200[1,-70,70]"' \
        --PO '"map=^.*/ggH_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25:r_ggH_GG2H_GE2J_PTH_0_200[1,-70,70]"' \
        --PO '"map=^.*/ggH_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25:r_ggH_GG2H_GE2J_PTH_0_200[1,-70,70]"' \
        --PO '"map=^.*/qqH_QQ2HQQ_FWDH:r_qqH_QQ2HQQ_LE1J[1,-70,70]"' \
        --PO '"map=^.*/qqH_QQ2HQQ_0J:r_qqH_QQ2HQQ_LE1J[1,-70,70]"' \
        --PO '"map=^.*/qqH_QQ2HQQ_1J:r_qqH_QQ2HQQ_LE1J[1,-70,70]"' \
        --PO '"map=^.*/qqH_QQ2HQQ_GE2J_MJJ_0_60:r_qqH_QQ2HQQ_GE2J_MJJ_0_350[1,-70,70]"' \
        --PO '"map=^.*/qqH_QQ2HQQ_GE2J_MJJ_60_120:r_qqH_QQ2HQQ_GE2J_MJJ_0_350[1,-70,70]"' \
        --PO '"map=^.*/qqH_QQ2HQQ_GE2J_MJJ_120_350:r_qqH_QQ2HQQ_GE2J_MJJ_0_350[1,-70,70]"' \
        --PO '"map=^.*/qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200:r_qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200[1,-70,70]"' \
        --PO '"map=^.*/qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25:r_qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_0_200[1,-70,70]"' \
        --PO '"map=^.*/qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25:r_qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_0_200[1,-70,70]"' \
        --PO '"map=^.*/qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25:r_qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_0_200[1,-70,70]"' \
        --PO '"map=^.*/qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25:r_qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_0_200[1,-70,70]"' | tee $LOGFILE
fi
