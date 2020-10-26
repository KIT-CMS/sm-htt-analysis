#!/bin/bash
ERA=$1
CHANNEL=$2
VARIABLE=$3

source utils/setup_cmssw.sh
mkdir plots/limits/${ERA}/${CHANNEL} -p
if [ "$ERA" -eq 2016 ]; then
    ERA_STRING="35.9 fb^{-1} (2016, 13 TeV)"
fi
if [ "$ERA" -eq 2017 ]; then
    ERA_STRING="41.5 fb^{-1} (2017, 13 TeV)"
fi
if [ "$ERA" -eq 2018 ]; then
    ERA_STRING="59.7 fb^{-1} (2018, 13 TeV)"
fi
if [ "$ERA" = "combined" ]; then
    ERA_STRING="137.2 fb^{-1} (13 TeV)"
fi

if [ "$CHANNEL" == "all" ]; then

    for MASS in  240 280 320 360 400 450 500 550 600 700 800 900 1000 1200 1400 1600 1800 2000 2500 3000
    do
        if [ "$MASS" -lt 1001 ]; then
            IN_JSON=""
            for MASS_H2 in 60 70 75 80 85 90 95 100 110 120 130 150 170 190 250 300 350 400 450 500 550 600 650 700 750 800 850
            do
                SUM=$((MASS_H2+125))
                if [ "$SUM" -gt "$MASS" ]
                then
                    continue  
                fi
                IN_JSON="${IN_JSON} /storage/gridka-nrg/jbechtel/gc_storage/nmssm_limits/2020_09_21/medium/retrain_cutonChi2/${ERA}/${CHANNEL}/nmssm_combined_${CHANNEL}_${MASS}_${MASS_H2}_cmb.json"   

                IN_JSON_400="${IN_JSON_400} /storage/gridka-nrg/jbechtel/gc_storage/nmssm_limits/2020_09_26/medium/retrain_400/${ERA}/${CHANNEL}/nmssm_combined_${CHANNEL}_${MASS}_${MASS_H2}_cmb.json"   

                IN_JSON_450="${IN_JSON_450} /storage/gridka-nrg/jbechtel/gc_storage/nmssm_limits/2020_09_26/medium/retrain_450/${ERA}/${CHANNEL}/nmssm_combined_${CHANNEL}_${MASS}_${MASS_H2}_cmb.json"   


            done

            python merge_json.py --input $IN_JSON --output limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json
            python merge_json.py --input $IN_JSON_400 --output limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_400_cmb.json
            python merge_json.py --input $IN_JSON_450 --output limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_450_cmb.json

            python select_optimal_json.py --input limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_400_cmb.json limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_450_cmb.json --output limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb_optimal.json

            python plot_2d_limits.py -e $ERA -c $CHANNEL -o plots/limits/${ERA}/${CHANNEL}    

            plotMSSMLimits.py limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb_optimal.json --cms-sub "Own Work" --title-right "$ERA_STRING" --y-axis-min 0.0001 --y-axis-max 200.0  --show exp  --output plots/limits/${ERA}/${CHANNEL}/nmssm_${ERA}_${CHANNEL}_${MASS}_v2 --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 800.0  --logx 
        else
            IN_JSON=""
            for MASS_H2 in 60 70 80 90 100 120 150 170 190 250 300 350 400 450 500 550 600 650 700 800 900 1000 1100 1200 1300 1400 1600 1800 2000 2200 2400 2600 2800
            do
                SUM=$((MASS_H2+125))
                if [ "$SUM" -gt "$MASS" ]
                then
                    continue  
                fi
                IN_JSON="${IN_JSON} /storage/gridka-nrg/jbechtel/gc_storage/nmssm_limits/2020_09_21/medium/retrain_cutonChi2/${ERA}/${CHANNEL}/nmssm_combined_${CHANNEL}_${MASS}_${MASS_H2}_cmb.json"   

                IN_JSON_400="${IN_JSON_400} /storage/gridka-nrg/jbechtel/gc_storage/nmssm_limits/2020_09_26/medium/retrain_400/${ERA}/${CHANNEL}/nmssm_combined_${CHANNEL}_${MASS}_${MASS_H2}_cmb.json"   

                IN_JSON_450="${IN_JSON_450} /storage/gridka-nrg/jbechtel/gc_storage/nmssm_limits/2020_09_26/medium/retrain_450/${ERA}/${CHANNEL}/nmssm_combined_${CHANNEL}_${MASS}_${MASS_H2}_cmb.json"   


            done

            python merge_json.py --input $IN_JSON --output limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json
            python merge_json.py --input $IN_JSON_400 --output limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_400_cmb.json
            python merge_json.py --input $IN_JSON_450 --output limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_450_cmb.json

            python select_optimal_json.py --input limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_400_cmb.json limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_450_cmb.json --output limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb_optimal.json


            plotMSSMLimits.py limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb_optimal.json --cms-sub "Own Work" --title-right "$ERA_STRING" --y-axis-min 0.0001 --y-axis-max 200.0  --show exp  --output plots/limits/${ERA}/${CHANNEL}/nmssm_${ERA}_${CHANNEL}_${MASS}_v2 --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 2800.0  --logx 
    fi
    done

else

    for MASS in  240 280 320 360 400 450 500 550 600 700 800 900 1000 1200 1400 1600 1800 2000 2500 3000
    do
        if [ "$MASS" -lt 1001 ]; then
            IN_JSON=""
            for MASS_H2 in 60 70 75 80 85 90 95 100 110 120 130 150 170 190 250 300 350 400 450 500 550 600 650 700 750 800 850
            do
                SUM=$((MASS_H2+125))
                if [ "$SUM" -gt "$MASS" ]
                then
                    continue  
                fi
                IN_JSON="${IN_JSON} /storage/gridka-nrg/jbechtel/gc_storage/nmssm_limits/2020_09_21/medium/retrain_cutonChi2/${ERA}/${CHANNEL}/nmssm_${CHANNEL}_${MASS}_${MASS_H2}_cmb.json" 

            done

            python merge_json.py --input $IN_JSON --output limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json

            plotMSSMLimits.py limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json --cms-sub "Own Work" --title-right "$ERA_STRING" --y-axis-min 0.0001 --y-axis-max 500.0  --show exp  --output plots/limits/${ERA}/${CHANNEL}/nmssm_${ERA}_${CHANNEL}_${MASS} --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 800.0  --logx 
        else
            IN_JSON=""
            for MASS_H2 in 60 70 80 90 100 120 150 170 190 250 300 350 400 450 500 550 600 650 700 800 900 1000 1100 1200 1300 1400 1600 1800 2000 2200 2400 2600 2800
            do
                SUM=$((MASS_H2+125))
                if [ "$SUM" -gt "$MASS" ]
                then
                    continue  
                fi
                IN_JSON="${IN_JSON} /storage/gridka-nrg/jbechtel/gc_storage/nmssm_limits/2020_09_21/medium/retrain_cutonChi2/${ERA}/${CHANNEL}/nmssm_${CHANNEL}_${MASS}_${MASS_H2}_cmb.json" 

            done

            python merge_json.py --input $IN_JSON --output limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json


            plotMSSMLimits.py limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json --cms-sub "Own Work" --title-right "$ERA_STRING"  --y-axis-min 0.0001 --y-axis-max 500.0  --show exp  --output plots/limits/${ERA}/${CHANNEL}/nmssm_${ERA}_${CHANNEL}_${MASS} --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 2800.0  --logx 
    fi
    done

fi

fi
