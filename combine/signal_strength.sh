#!/bin/bash

ERA=$1
STXS_SIGNALS=$2

source utils/setup_cmssw.sh

if [ $STXS_SIGNALS == 0 ]
then
    # Fit
    combine -M MaxLikelihoodFit -m 125 ${ERA}_workspace.root --robustFit 1 -n $ERA
fi

if [ $STXS_SIGNALS == 1 ]
then
    # Produce workspace with redefined signals
    combineTool.py \
        -M T2W \
        -m 125 \
        -o ${ERA}_workspace_STXS_stage1.root \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=^.*/ggH125_0J.?$:r_ggH_0J[1,-30,30]"' \
        --PO '"map=^.*/ggH125_1J.?$:r_ggH_1J[1,-30,30]"' \
        --PO '"map=^.*/ggH125_GE2J.?$:r_ggH_GE2J[1,-30,30]"' \
        --PO '"map=^.*/ggH125_VBFTOPO.?$:r_ggH_VBFTOPO[1,-30,30]"' \
        --PO '"map=^.*/qqH125_VBFTOPO_JET3VETO.?$:r_qqH_VBFTOPO_JET3VETO[1,-30,30]"' \
        --PO '"map=^.*/qqH125_VBFTOPO_JET3.?$:r_qqH_VBFTOPO_JET3[1,-30,30]"' \
        --PO '"map=^.*/qqH125_REST.?$:r_qqH_REST[1,-30,30]"' \
        --PO '"map=^.*/qqH125_PTJET1_GT200.?$:r_qqH_PTJET1_GT200[1,-30,30]"' \
        -i ${ERA}_workspace.root

    # Fit
    combineTool.py -M MultiDimFit -m 125 -d ${ERA}_workspace_STXS_stage1.root --algo singles --robustFit 1 -n $ERA
fi
