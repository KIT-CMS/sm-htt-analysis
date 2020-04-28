#!/bin/bash

ERA=$1
CHANNEL=$2
MASS=$3
VARIABLE=$4
MASS_H2=$5

source utils/setup_cmssw.sh

if [ "$CHANNEL" == "all" ]
    then
    MorphingMSSMvsSM --era=${ERA} --auto_rebin=1 --binomial_bbb=1 --variable=${VARIABLE} --analysis=nmssm --channel="mt et tt em" --heavy_mass=${MASS}  --light_mass=${MASS_H2} --output_folder="output_"${CHANNEL}
    else
    MorphingMSSMvsSM --era=${ERA} --auto_rebin=1 --binomial_bbb=1 --variable=${VARIABLE} --analysis=nmssm --channel=${CHANNEL} --heavy_mass=${MASS} --light_mass=${MASS_H2} --output_folder="output_"${CHANNEL}
fi
combineTool.py -M T2W -o "ws.root"  --PO '"map=^.*/NMSSM_'${MASS}'_125_'${MASS_H2}'$:r_NMSSM_'${MASS}'_125_'${MASS_H2}'[0,0,200]"' -i output_${CHANNEL}_nmssm_${VARIABLE}_${MASS}_${MASS_H2}/${ERA}/cmb/ -m ${MASS_H2} --parallel 2 -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel

combineTool.py -m $MASS_H2 -M AsymptoticLimits --rAbsAcc 0 --rRelAcc 0.0005  --setParameters r_NMSSM_${MASS}_125_${MASS_H2}=0 --redefineSignalPOIs r_NMSSM_${MASS}_125_${MASS_H2} -d output_${CHANNEL}_nmssm_${VARIABLE}_${MASS}_${MASS_H2}/${ERA}/cmb/ws.root --there -n ".NMSSM_"${MASS}"_125_"  --task-name NMSSM_${MASS}_125_${MASS_H2} --parallel 2

combineTool.py -M CollectLimits output_${CHANNEL}_nmssm_${VARIABLE}_${MASS}_${MASS_H2}/${ERA}/cmb/higgsCombine*.root --use-dirs -o nmssm_${CHANNEL}_${VARIABLE}_${MASS}_${MASS_H2}.json