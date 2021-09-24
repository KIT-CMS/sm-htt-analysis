#!/bin/bash
set -e
source utils/setup_cmssw.sh
source utils/setup_python.sh

[[ ! -z $1 && ! -z $2 && ! -z $3 ]] || (echo Invalid number of arguments; exit 1  )
ERA=$1
STXS_FIT=$2
TAG=$3
NUM_THREADS=12

if [[ $STXS_FIT == "inclusive" || $STXS_FIT == "stxs_stage0" ]]; then
    STXS_SIGNALS=stxs_stage0
elif [[ $STXS_FIT == "stxs_stage1p1" ]] ; then
    STXS_SIGNALS=stxs_stage1p1
fi

LOGFILE=output/log/workspace-${ERA}-$STXS_FIT-${TAG}.log

# Collect input directories for eras and define output path for workspace
INPUT=output/datacards/${ERA}-${TAG}-smhtt-ML/${STXS_SIGNALS}/*/125
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
    combineTool.py -M T2W -o ${OUTPUT} -i ${INPUT} --parallel $NUM_THREADS --channel-masks | tee $LOGFILE
    for channel in "et" "mt" "tt" "em"; do
        INPUT=output/datacards/${ERA}-${TAG}-smhtt-ML/${STXS_SIGNALS}/${channel}/125
        OUTPUT=${ERA}-${STXS_FIT}-${channel}-workspace.root
        combineTool.py -M T2W -o ${OUTPUT} -i ${INPUT} --parallel $NUM_THREADS --channel-masks | tee $LOGFILE
    done
fi
if [ $STXS_FIT == "stxs_stage0" ]; then
    combineTool.py -M T2W -o ${OUTPUT} -i ${INPUT} --parallel $NUM_THREADS \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=^.*/ggH_htt.?$:r_ggH[1,-5,5]"' \
        --PO '"map=^.*/ggZH_had_htt.?$:r_ggH[1,-5,5]"' \
        --PO '"map=^.*/WH_had_htt.?$:r_qqH[1,-5,5]"' \
        --PO '"map=^.*/ZH_had_htt.?$:r_qqH[1,-5,5]"' \
        --PO '"map=^.*/qqH_htt.?$:r_qqH[1,-5,5]"' \
        --PO '"map=^.*/WH_lep_htt.?$:r_VH[1,-5,7]"' \
       	--PO '"map=^.*/ZH_lep_htt.?$:r_VH[1,-5,7]"' \
        --PO '"map=^.*/ggZH_lep_htt.?$:r_VH[1,-5,7]"' | tee $LOGFILE
fi

# Stage 1.1 as unified for the MC production, see https://indico.cern.ch/event/820874/contributions/3431583/attachments/1843868/3024330/Legacy_SM_H_-_Status.pdf, Slide 4
if [ $STXS_FIT == "stxs_stage1p1" ]; then
    combineTool.py -M T2W -o ${OUTPUT} -i ${INPUT} --parallel $NUM_THREADS \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=^.*/ggH_FWDH_htt:r_ggH_GG2H_0J_PTH_0_10[1,-20,20]"' \
        --PO '"map=^.*/ggH_PTH_200_300_htt:r_ggH_GG2H_PTH_200_300[1,-20,20]"' \
        --PO '"map=^.*/ggH_PTH_300_450_htt:r_ggH_GG2H_PTH_GT300[1,-20,20]"' \
        --PO '"map=^.*/ggH_PTH_450_650_htt:r_ggH_GG2H_PTH_GT300[1,-20,20]"' \
        --PO '"map=^.*/ggH_PTH_GT650_htt:r_ggH_GG2H_PTH_GT300[1,-20,20]"' \
        --PO '"map=^.*/ggH_0J_PTH_0_10_htt:r_ggH_GG2H_0J_PTH_0_10[1,-20,20]"' \
        --PO '"map=^.*/ggH_0J_PTH_GT10_htt:r_ggH_GG2H_0J_PTH_GT10[1,-20,20]"' \
        --PO '"map=^.*/ggH_1J_PTH_0_60_htt:r_ggH_GG2H_1J_PTH_0_60[1,-20,20]"' \
        --PO '"map=^.*/ggH_1J_PTH_60_120_htt:r_ggH_GG2H_1J_PTH_60_120[1,-20,20]"' \
        --PO '"map=^.*/ggH_1J_PTH_120_200_htt:r_ggH_GG2H_1J_PTH_120_200[1,-20,20]"' \
        --PO '"map=^.*/ggH_GE2J_MJJ_0_350_PTH_0_60_htt:r_ggH_GG2H_GE2J[1,-20,20]"' \
        --PO '"map=^.*/ggH_GE2J_MJJ_0_350_PTH_60_120_htt:r_ggH_GG2H_GE2J[1,-20,20]"' \
        --PO '"map=^.*/ggH_GE2J_MJJ_0_350_PTH_120_200_htt:r_ggH_GG2H_GE2J[1,-20,20]"' \
        --PO '"map=^.*/ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_htt:r_ggH_GG2H_GE2J[1,-20,20]"' \
        --PO '"map=^.*/ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_htt:r_ggH_GG2H_GE2J[1,-20,20]"' \
        --PO '"map=^.*/ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_htt:r_ggH_GG2H_GE2J[1,-20,20]"' \
        --PO '"map=^.*/ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_htt:r_ggH_GG2H_GE2J[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_FWDH_htt:r_ggH_GG2H_0J_PTH_0_10[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_PTH_200_300_htt:r_ggH_GG2H_PTH_200_300[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_PTH_300_450_htt:r_ggH_GG2H_PTH_GT300[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_PTH_450_650_htt:r_ggH_GG2H_PTH_GT300[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_PTH_GT650_htt:r_ggH_GG2H_PTH_GT300[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_0J_PTH_0_10_htt:r_ggH_GG2H_0J_PTH_0_10[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_0J_PTH_GT10_htt:r_ggH_GG2H_0J_PTH_GT10[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_1J_PTH_0_60_htt:r_ggH_GG2H_1J_PTH_0_60[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_1J_PTH_60_120_htt:r_ggH_GG2H_1J_PTH_60_120[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_1J_PTH_120_200_htt:r_ggH_GG2H_1J_PTH_120_200[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_GE2J_MJJ_0_350_PTH_0_60_htt:r_ggH_GG2H_GE2J[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_GE2J_MJJ_0_350_PTH_60_120_htt:r_ggH_GG2H_GE2J[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_GE2J_MJJ_0_350_PTH_120_200_htt:r_ggH_GG2H_GE2J[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_htt:r_ggH_GG2H_GE2J[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_htt:r_ggH_GG2H_GE2J[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_htt:r_ggH_GG2H_GE2J[1,-20,20]"' \
        --PO '"map=^.*/ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_htt:r_ggH_GG2H_GE2J[1,-20,20]"' \
        --PO '"map=^.*/qqH_FWDH_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/qqH_0J_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/qqH_1J_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/qqH_GE2J_MJJ_0_60_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/qqH_GE2J_MJJ_60_120_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/qqH_GE2J_MJJ_120_350_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/qqH_GE2J_MJJ_GT350_PTH_GT200_htt:r_qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200[1,-20,20]"' \
        --PO '"map=^.*/qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_htt:r_qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200[1,-20,20]"' \
        --PO '"map=^.*/qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_htt:r_qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200[1,-20,20]"' \
        --PO '"map=^.*/qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_htt:r_qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200[1,-20,20]"' \
        --PO '"map=^.*/qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_htt:r_qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200[1,-20,20]"' \
        --PO '"map=^.*/WH_had_FWDH_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/WH_had_0J_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/WH_had_1J_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/WH_had_GE2J_MJJ_0_60_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/WH_had_GE2J_MJJ_60_120_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/WH_had_GE2J_MJJ_120_350_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/WH_had_GE2J_MJJ_GT350_PTH_GT200_htt:r_qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200[1,-20,20]"' \
        --PO '"map=^.*/WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_htt:r_qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200[1,-20,20]"' \
        --PO '"map=^.*/WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_htt:r_qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200[1,-20,20]"' \
        --PO '"map=^.*/WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_htt:r_qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200[1,-20,20]"' \
        --PO '"map=^.*/WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_htt:r_qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200[1,-20,20]"' \
        --PO '"map=^.*/ZH_had_FWDH_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/ZH_had_0J_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/ZH_had_1J_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/ZH_had_GE2J_MJJ_0_60_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/ZH_had_GE2J_MJJ_60_120_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/ZH_had_GE2J_MJJ_120_350_htt:r_qqH_QQ2HQQ_noVBFtopo[1,-20,20]"' \
        --PO '"map=^.*/ZH_had_GE2J_MJJ_GT350_PTH_GT200_htt:r_qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200[1,-20,20]"' \
        --PO '"map=^.*/ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25_htt:r_qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200[1,-20,20]"' \
        --PO '"map=^.*/ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25_htt:r_qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200[1,-20,20]"' \
        --PO '"map=^.*/ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25_htt:r_qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200[1,-20,20]"' \
        --PO '"map=^.*/ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25_htt:r_qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200[1,-20,20]"' \
       	--PO '"map=^.*/WH_lep_FWDH_htt:r_WH_PTV_0_150[1,-20,20]"' \
       	--PO '"map=^.*/WH_lep_PTV_0_75_htt:r_WH_PTV_0_150[1,-20,20]"' \
       	--PO '"map=^.*/WH_lep_PTV_75_150_htt:r_WH_PTV_0_150[1,-20,20]"' \
       	--PO '"map=^.*/WH_lep_PTV_150_250_0J_htt:r_WH_PTV_GT150[1,-20,20]"' \
       	--PO '"map=^.*/WH_lep_PTV_150_250_GE1J_htt:r_WH_PTV_GT150[1,-20,20]"' \
       	--PO '"map=^.*/WH_lep_PTV_GT250_htt:r_WH_PTV_GT150[1,-20,20]"' \
       	--PO '"map=^.*/ZH_lep_FWDH_htt:r_ZH_PTV_0_150[1,-20,20]"' \
      	--PO '"map=^.*/ZH_lep_PTV_0_75_htt:r_ZH_PTV_0_150[1,-20,20]"' \
       	--PO '"map=^.*/ZH_lep_PTV_75_150_htt:r_ZH_PTV_0_150[1,-20,20]"' \
       	--PO '"map=^.*/ZH_lep_PTV_150_250_0J_htt:r_ZH_PTV_GT150[1,-20,20]"' \
       	--PO '"map=^.*/ZH_lep_PTV_150_250_GE1J_htt:r_ZH_PTV_GT150[1,-20,20]"' \
       	--PO '"map=^.*/ZH_lep_PTV_GT250_htt:r_ZH_PTV_GT150[1,-20,20]"' \
       	--PO '"map=^.*/ggZH_lep_FWDH_htt:r_ZH_PTV_0_150[1,-20,20]"' \
       	--PO '"map=^.*/ggZH_lep_PTV_0_75_htt:r_ZH_PTV_0_150[1,-20,20]"' \
       	--PO '"map=^.*/ggZH_lep_PTV_75_150_htt:r_ZH_PTV_0_150[1,-20,20]"' \
       	--PO '"map=^.*/ggZH_lep_PTV_150_250_0J_htt:r_ZH_PTV_GT150[1,-20,20]"' \
       	--PO '"map=^.*/ggZH_lep_PTV_150_250_GE1J_htt:r_ZH_PTV_GT150[1,-20,20]"' \
       	--PO '"map=^.*/ggZH_lep_PTV_GT250_ht:r_ZH_PTV_GT150[1,-20,20]"' | tee $LOGFILE
fi
