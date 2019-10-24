#!/bin/bash

CHANNEL=$1
STEP=$2

for CHANNEL in mt et tt all
do

if [ "$STEP" -lt 1 ]
then
    if [ "$CHANNEL" == "all" ]
    then
    ./cutbased_shapes/produce_shapes.sh 8 2017 diBJetMass backgrounds mt & 
    ./cutbased_shapes/produce_shapes.sh 8 2017 diBJetMass signals mt & 
    ./cutbased_shapes/produce_shapes.sh 8 2017 diBJetMass backgrounds et & 
    ./cutbased_shapes/produce_shapes.sh 8 2017 diBJetMass signals et & 
    ./cutbased_shapes/produce_shapes.sh 8 2017 diBJetMass backgrounds tt & 
    ./cutbased_shapes/produce_shapes.sh 8 2017 diBJetMass signals tt & 
    else
    ./cutbased_shapes/produce_shapes.sh 8 2017 diBJetMass backgrounds $CHANNEL & 
    ./cutbased_shapes/produce_shapes.sh 8 2017 diBJetMass signals $CHANNEL &  
    fi

    wait

    ./cutbased_shapes/normalize_ff_and_sync_shapes.sh

    cp htt_*nmssm*-Run2017-diBJetMass.root /portal/ekpbms1/home/jbechtel/postprocessing/sm-htt-analysis/CMSSW_10_2_16_UL/src/CombineHarvester/MSSMvsSMRun2Legacy/shapes/.
fi

if [ "$STEP" -lt 2 ]
then

    source utils/setup_cmssw.sh

    rm -rf output_*

    for MASS in 320 450 700 800 900 1000
    do
        LIGHT_MASSES=""
        for MASS_H2 in 60 70 75 80 85 90 95 100 110 120 130 150 170 190 250 300 350 400 450 500 550 600 650 700 750 800 850
        do
            SUM=$((MASS_H2+125))
            if [ "$SUM" -gt "$MASS" ]
            then
            continue  
            fi
            LIGHT_MASSES="${LIGHT_MASSES}${MASS_H2},"
        done

        LIGHT_MASSES=${LIGHT_MASSES::-1}

        ./create_limit_nmssm.sh $CHANNEL $MASS $LIGHT_MASSES &     
    done 
fi

wait

if [ "$STEP" -lt 3 ]
then
    for MASS in 320 450 700 800 900 1000
    do
        source utils/setup_cmssw.sh
        plotMSSMLimits.py --cms-sub "Private Work" --title-right "41.5 fb^{-1} (2017, 13 TeV)"   --y-axis-min 0.001 --y-axis-max 500.0 --show exp nmssm_${CHANNEL}_${MASS}_cmb.json  --output nmssm_${MASS}_${CHANNEL} --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 850.0 &
    done
    wait
fi
done
