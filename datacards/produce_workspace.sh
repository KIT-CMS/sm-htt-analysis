#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1
STXS_FIT=$2

NUM_THREADS=8

# Collect input directories for eras and define output path for workspace
INPUT=output/${ERA}_smhtt/cmb/125
echo "[INFO] Add datacards to workspace from path "${INPUT}"."

OUTPUT=${PWD}/${ERA}_workspace.root
echo "[INFO] Write workspace to "${OUTPUT}"."

# Clean previous workspace
rm -f $OUTPUT

# Define signals to be fitted and produce workspace
if [ $STXS_FIT == "inclusive" ]; then
    combineTool.py -M T2W -o ${OUTPUT} -i ${INPUT} --parallel $NUM_THREADS
fi
if [ $STXS_FIT == "stxs_stage0" ]; then
    combineTool.py -M T2W -o ${OUTPUT} -i ${INPUT} --parallel $NUM_THREADS \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=^.*/ggH.?$:r_ggH[1,-5,5]"' \
        --PO '"map=^.*/qqH.?$:r_qqH[1,-5,5]"'
fi
if [ $STXS_FIT == "stxs_stage1" ]; then
    combineTool.py -M T2W -o ${OUTPUT} -i ${INPUT} --parallel $NUM_THREADS \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=^.*/ggH_0J.?$:r_ggH_0J[1,-30,30]"' \
        --PO '"map=^.*/ggH_1J_PTH_0_60.?$:r_ggH_1J_PTH_0_60[1,-30,30]"' \
        --PO '"map=^.*/ggH_1J_PTH_60_120.?$:r_ggH_1J_PTH_60_120[1,-30,30]"' \
        --PO '"map=^.*/ggH_1J_PTH_120_200.?$:r_ggH_1J_PTH_120_200[1,-30,30]"' \
        --PO '"map=^.*/ggH_1J_PTH_GT200.?$:r_ggH_1J_PTH_GT200[1,-30,30]"' \
        --PO '"map=^.*/ggH_GE2J_PTH_0_60.?$:r_ggH_GE2J_PTH_0_60[1,-30,30]"' \
        --PO '"map=^.*/ggH_GE2J_PTH_60_120.?$:r_ggH_GE2J_PTH_60_120[1,-30,30]"' \
        --PO '"map=^.*/ggH_GE2J_PTH_120_200.?$:r_ggH_GE2J_PTH_120_200[1,-30,30]"' \
        --PO '"map=^.*/ggH_GE2J_PTH_GT200.?$:r_ggH_GE2J_PTH_GT200[1,-30,30]"' \
        --PO '"map=^.*/ggH_VBFTOPO_JET3.?$:r_ggH_VBFTOPO_JET3[1,-30,30]"' \
        --PO '"map=^.*/ggH_VBFTOPO_JET3VETO.?$:r_ggH_VBFTOPO_JET3VETO[1,-30,30]"' \
        --PO '"map=^.*/qqH_VBFTOPO_JET3VETO.?$:r_qqH_VBFTOPO_JET3VETO[1,-30,30]"' \
        --PO '"map=^.*/qqH_VBFTOPO_JET3.?$:r_qqH_VBFTOPO_JET3[1,-30,30]"' \
        --PO '"map=^.*/qqH_REST.?$:r_qqH_REST[1,-30,30]"' \
        --PO '"map=^.*/qqH_VH2JET.?$:r_qqH_VH2JET[1,-100,100]"' \
        --PO '"map=^.*/qqH_PTJET1_GT200.?$:r_qqH_PTJET1_GT200[1,-30,30]"'
fi
