#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1
STXS_SIGNALS=$2
STXS_CATEGORIES=$3
STXS_FIT=$4
JETFAKES=$5
EMBEDDING=$6
VARIABLE=$7
CHANNELS=${@:8}

NUM_THREADS=8

#USE_DATACARDPRODUCER=1
if [ -n "$USE_DATACARDPRODUCER" ]; then
    python datacards/produce_datacard.py \
        --era $ERA \
        --channels $CHANNELS \
        --stxs-signals $STXS_SIGNALS \
        --stxs-categories $CATEGORIES \
        --shapes ${ERA}_shapes.root

    combineTool.py -M T2W -o ${ERA}_workspace.root -i ${ERA}_datacard.txt -m 125.0 --parallel $NUM_THREADS
fi

USE_COMBINEHARVESTER=1
if [ -n "$USE_COMBINEHARVESTER" ]; then
    # Remove output directory
    rm -rf output/ ${ERA}_workspace.root
    INPUT_FOLDER="../../../../.."

    # Create datacards
    $CMSSW_BASE/bin/slc7_amd64_gcc700/MorphingSMRun2Legacy \
        --input_folder_mt=$INPUT_FOLDER \
        --input_folder_et=$INPUT_FOLDER \
        --input_folder_tt=$INPUT_FOLDER \
        --input_folder_em=$INPUT_FOLDER \
        --real_data=true \
        --jetfakes=$JETFAKES \
        --embedding=$EMBEDDING \
        --postfix="-ML" \
        --channel="${CHANNELS}" \
        --auto_rebin=true \
        --rebin_categories=false \
        --gof_category_name ${CHANNELS}_${VARIABLE} \
        --stxs_signals=$STXS_SIGNALS \
        --categories=$STXS_CATEGORIES \
        --era=$ERA \
        --output="${ERA}_smhtt" 
        
    # Merge datacards to workspace and define signals to be fitted
    DATACARD_PATH=output/${ERA}_smhtt/cmb/125
    if [ $STXS_FIT == "inclusive" ]; then
        combineTool.py -M T2W -o workspace.root -i ${DATACARD_PATH} --parallel $NUM_THREADS
    fi
    if [ $STXS_FIT == "stxs_stage0" ]; then
        combineTool.py -M T2W -o workspace.root -i ${DATACARD_PATH} --parallel $NUM_THREADS \
            -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
            --PO '"map=^.*/ggH.?$:r_ggH[1,-5,5]"' \
            --PO '"map=^.*/qqH.?$:r_qqH[1,-5,5]"'
    fi
    if [ $STXS_FIT == "stxs_stage1" ]; then
        combineTool.py -M T2W -o workspace.root -i ${DATACARD_PATH} --parallel $NUM_THREADS \
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
    cp $DATACARD_PATH/workspace.root ${ERA}_workspace.root
fi
