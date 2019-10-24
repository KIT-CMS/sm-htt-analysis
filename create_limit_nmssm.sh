#!/bin/bash

CHANNEL=$1
MASS=$2
LIGHT_MASSES=$3

if [ "$CHANNEL" == "all" ]
    then
    MorphingMSSMvsSM --era=2017 --auto_rebin=1 --binomial_bbb=1 --variable=diBJetMass --analysis=nmssm --channel="mt et tt" --heavy_mass=${MASS}
    else
    MorphingMSSMvsSM --era=2017 --auto_rebin=1 --binomial_bbb=1 --variable=diBJetMass --analysis=nmssm --channel=${CHANNEL} --heavy_mass=${MASS}
fi
combineTool.py -M T2W -o "ws.root" -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO '"map=^.*/NMSSM_'${MASS}'_125_$:r_NMSSM_'${MASS}'_125_[0,0,200]"' -i output_nmssm_diBJetMass_${MASS}/Run2017/cmb/ -m 100 --parallel 8

combineTool.py -m $LIGHT_MASSES -M AsymptoticLimits --rAbsAcc 0 --rRelAcc 0.0005  --setParameters r_NMSSM_${MASS}_125_=0 --redefineSignalPOIs r_NMSSM_${MASS}_125_ -d output_nmssm_diBJetMass_${MASS}/Run2017/cmb/ws.root --there -n ".NMSSM_"${MASS}"_125_"  --task-name NMSSM_${MASS}_125_ --parallel 8

combineTool.py -M CollectLimits output_nmssm_diBJetMass_${MASS}/Run2017/cmb/higgsCombine*.root --use-dirs -o nmssm_${CHANNEL}_${MASS}.json
