#!/bin/bash
ERA=$1
CHANNEL=$2
VARIABLE=$3
STEP=$4

if [ "$STEP" -lt 1 ]
then
    if [ "$VARIABLE" == "nmssm_discriminator" ]; then
        for TEMP_VAR in m_vis mbb m_ttvisbb
        do
            if [ "$CHANNEL" == "all" ]; then
            ./shapes/produce_nmssm_shapes.sh ${ERA} mt ${TEMP_VAR} 4 & 
            ./shapes/produce_nmssm_shapes.sh ${ERA} et ${TEMP_VAR} 4 & 
            ./shapes/produce_nmssm_shapes.sh ${ERA} tt ${TEMP_VAR} 4 &
            ./shapes/produce_nmssm_shapes.sh ${ERA} em ${TEMP_VAR} 4 &

            wait
            else
            ./shapes/produce_nmssm_shapes.sh ${ERA} ${CHANNEL} ${TEMP_VAR} 32 &
            fi
        done
        wait
        ./shapes/create_nmssm_discriminator.sh ${ERA} ${CHANNEL} ${VARIABLE}
        echo "1"
    else
        if [ "$CHANNEL" == "all" ]; then
        ./shapes/produce_nmssm_shapes.sh ${ERA} mt ${VARIABLE} 8 & 
        ./shapes/produce_nmssm_shapes.sh ${ERA} et ${VARIABLE} 8 & 
        ./shapes/produce_nmssm_shapes.sh ${ERA} tt ${VARIABLE} 8 &
        ./shapes/produce_nmssm_shapes.sh ${ERA} em ${VARIABLE} 8 & 

        wait
        else
        #./shapes/produce_nmssm_shapes.sh ${ERA} ${CHANNEL} ${VARIABLE} 1
	echo 1
        fi
    fi
    
    # ./shapes/create_nmssm_discriminator.sh ${ERA} ${CHANNEL} ${VARIABLE}

    ./shapes/normalize_ff_and_sync_shapes.sh ${ERA} ${CHANNEL} ${VARIABLE}

    cp output/shapes/htt_${CHANNEL}.inputs-nmssm-${ERA}-${VARIABLE}.root ${PWD}/CMSSW_10_2_16_UL/src/CombineHarvester/MSSMvsSMRun2Legacy/shapes/.
    exit
fi
if [ "$STEP" -lt 2 ]
then


    # rm -r output_*
    for MASS in 240 280 320 360 400 450 500 550 600 700 800 900 1000 1200 1400 1600 1800 2000 2500 3000
    do
        if [ "$MASS" -lt 1001 ]; then
            for MASS_H2 in 60 70 75 80 85 90 95 100 110 120 130 150 170 190 250 300 350 400 450 500 550 600 650 700 750 800 850
            do
                SUM=$((MASS_H2+125))
                if [ "$SUM" -gt "$MASS" ]
                then
                continue  
                fi
                ./create_limit_nmssm.sh $ERA $CHANNEL $MASS $VARIABLE $MASS_H2 &
            done 
            wait
        else
            for MASS_H2 in 60 70 80 90 100 120 150 170 190 250 300 350 400 450 500 550 600 650 700 800 900 1000 1100 1200 1300 1400 1600 1800 2000 2200 2400 2600 2800
            do
                SUM=$((MASS_H2+125))
                if [ "$SUM" -gt "$MASS" ]
                then
                continue  
                fi
                ./create_limit_nmssm.sh $ERA $CHANNEL $MASS $VARIABLE $MASS_H2 &
            done 
            wait
        fi
    done 
fi

if [ "$STEP" -lt 3 ]
then
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
                    #IN_JSON="${IN_JSON} /storage/gridka-nrg/jbechtel/gc_storage/nmssm_limits/2020_09_08/mbb/${ERA}/${CHANNEL}/nmssm_combined${CHANNEL}_${MASS}_${MASS_H2}_cmb.json" 
                    IN_JSON="${IN_JSON} /storage/gridka-nrg/jbechtel/gc_storage/nmssm_limits/2020_09_08/medium/retrain_cutonChi2/${ERA}/${CHANNEL}/nmssm_combined_${CHANNEL}_${MASS}_${MASS_H2}_cmb.json"   
 
                done

                python merge_json.py --input $IN_JSON --output limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json

                python plot_2d_limits.py -e $ERA -c $CHANNEL -o plots/limits/${ERA}/${CHANNEL}    

                compare_limits.py  limit_jsons/nmssm_${ERA}_et_${MASS}_cmb.json:exp0:Title='e#tau_{h}',LineStyle=1,LineWidth=2,LineColor=46,MarkerSize=0 limit_jsons/nmssm_${ERA}_mt_${MASS}_cmb.json:exp0:Title='#mu_{}#tau_{h}',LineStyle=1,LineWidth=2,LineColor=8,MarkerSize=0 limit_jsons/nmssm_${ERA}_tt_${MASS}_cmb.json:exp0:Title='#tau_{h}#tau_{h}',LineStyle=1,LineWidth=2,LineColor=9,MarkerSize=0 limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json:exp0:Title='e#tau_{h}+#mu_{}^{}#tau_{h}+#tau_{h}#tau_{h}',LineStyle=1,LineWidth=2,LineColor=1,MarkerSize=0 --cms-sub "Own Work" --title-right "$ERA_STRING"  --y-axis-min 0.0001 --y-axis-max 200.0 --show exp   --output plots/limits/${ERA}/${CHANNEL}/nmssm_${ERA}_${CHANNEL}_compare_${MASS} --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 800.0  --logx  #--draw-theory

                #compare_limits.py  ../retrain_uncorrUnc/limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json:exp0:Title='Inclusive',LineStyle=1,LineWidth=2,LineColor=46,MarkerSize=0 limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json:exp0:Title='#splitline{Remove events}{with nonconv. kin.fit}',LineStyle=1,LineWidth=2,LineColor=8,MarkerSize=0 --cms-sub "Own Work" --title-right "$ERA_STRING"  --y-axis-min 0.0001 --y-axis-max 200.0 --show exp   --output plots/limits/${ERA}/${CHANNEL}/nmssm_${ERA}_${CHANNEL}_compare_${MASS} --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 800.0  --logx  #--draw-theory 

                plotMSSMLimits.py limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json --cms-sub "Own Work" --title-right "$ERA_STRING" --y-axis-min 0.0001 --y-axis-max 200.0  --show exp  --output plots/limits/${ERA}/${CHANNEL}/nmssm_${ERA}_${CHANNEL}_${MASS}_cutonChi2 --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 800.0  --logx 
            else
                IN_JSON=""
                for MASS_H2 in 60 70 80 90 100 120 150 170 190 250 300 350 400 450 500 550 600 650 700 800 900 1000 1100 1200 1300 1400 1600 1800 2000 2200 2400 2600 2800
                do
                    SUM=$((MASS_H2+125))
                    if [ "$SUM" -gt "$MASS" ]
                    then
                        continue  
                    fi
                    #IN_JSON="${IN_JSON} /storage/gridka-nrg/jbechtel/gc_storage/nmssm_limits/2020_09_08/mbb/${ERA}/${CHANNEL}/nmssm_combined${CHANNEL}_${MASS}_${MASS_H2}_cmb.json" 
                    IN_JSON="${IN_JSON} /storage/gridka-nrg/jbechtel/gc_storage/nmssm_limits/2020_09_08/medium/retrain_cutonChi2/${ERA}/${CHANNEL}/nmssm_combined_${CHANNEL}_${MASS}_${MASS_H2}_cmb.json" 


                done

                python merge_json.py --input $IN_JSON --output limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json

                python plot_2d_limits.py -e $ERA -c $CHANNEL -o plots/limits/${ERA}/${CHANNEL}    

                compare_limits.py  limit_jsons/nmssm_${ERA}_et_${MASS}_cmb.json:exp0:Title='e#tau_{h}',LineStyle=1,LineWidth=2,LineColor=46,MarkerSize=0 limit_jsons/nmssm_${ERA}_mt_${MASS}_cmb.json:exp0:Title='#mu_{}#tau_{h}',LineStyle=1,LineWidth=2,LineColor=8,MarkerSize=0 limit_jsons/nmssm_${ERA}_tt_${MASS}_cmb.json:exp0:Title='#tau_{h}#tau_{h}',LineStyle=1,LineWidth=2,LineColor=9,MarkerSize=0 limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json:exp0:Title='e#tau_{h}+#mu_{}^{}#tau_{h}+#tau_{h}#tau_{h}',LineStyle=1,LineWidth=2,LineColor=1,MarkerSize=0 --cms-sub "Own Work" --title-right "$ERA_STRING"  --y-axis-min 0.0001 --y-axis-max 200.0 --show exp   --output plots/limits/${ERA}/${CHANNEL}/nmssm_${ERA}_${CHANNEL}_compare_${MASS} --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 2800.0  --logx  #--draw-theory


                compare_limits.py  ../retrain_uncorrUnc/limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json:exp0:Title='Inclusive',LineStyle=1,LineWidth=2,LineColor=46,MarkerSize=0 limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json:exp0:Title='#splitline{Remove events}{with nonconv. kin.fit}',LineStyle=1,LineWidth=2,LineColor=8,MarkerSize=0 --cms-sub "Own Work" --title-right "$ERA_STRING"  --y-axis-min 0.0001 --y-axis-max 200.0 --show exp   --output plots/limits/${ERA}/${CHANNEL}/nmssm_${ERA}_${CHANNEL}_compare_${MASS} --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 2800.0  --logx  #--draw-theory 



                plotMSSMLimits.py limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json --cms-sub "Own Work" --title-right "$ERA_STRING" --y-axis-min 0.0001 --y-axis-max 200.0  --show exp  --output plots/limits/${ERA}/${CHANNEL}/nmssm_${ERA}_${CHANNEL}_${MASS}_cutonChi2 --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 2800.0  --logx 
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
                    IN_JSON="${IN_JSON} /storage/gridka-nrg/jbechtel/gc_storage/nmssm_limits/2020_09_08/medium/retrain_cutonChi2/${ERA}/${CHANNEL}/nmssm_${CHANNEL}_${MASS}_${MASS_H2}_cmb.json" 

                done

                python merge_json.py --input $IN_JSON --output limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json
                #python plot_2d_limits.py -e $ERA -c $CHANNEL -o plots/limits/${ERA}/${CHANNEL}    
                
                compare_limits.py  ../retrain_uncorrUnc/limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json:exp0:Title='Inclusive',LineStyle=1,LineWidth=2,LineColor=46,MarkerSize=0 limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json:exp0:Title='cut',LineStyle=1,LineWidth=2,LineColor=8,MarkerSize=0 --cms-sub "Own Work" --title-right "$ERA_STRING"  --y-axis-min 0.0001 --y-axis-max 200.0 --show exp   --output plots/limits/${ERA}/${CHANNEL}/nmssm_${ERA}_${CHANNEL}_compare_${MASS} --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 800.0  --logx  #--draw-theory 

                plotMSSMLimits.py limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json --cms-sub "Own Work" --title-right "$ERA_STRING" --y-axis-min 0.0001 --y-axis-max 500.0  --show exp  --output plots/limits/${ERA}/${CHANNEL}/nmssm_${ERA}_${CHANNEL}_${MASS}_cutonChi2 --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 800.0  --logx 
            else
                IN_JSON=""
                for MASS_H2 in 60 70 80 90 100 120 150 170 190 250 300 350 400 450 500 550 600 650 700 800 900 1000 1100 1200 1300 1400 1600 1800 2000 2200 2400 2600 2800
                do
                    SUM=$((MASS_H2+125))
                    if [ "$SUM" -gt "$MASS" ]
                    then
                        continue  
                    fi
                    IN_JSON="${IN_JSON} /storage/gridka-nrg/jbechtel/gc_storage/nmssm_limits/2020_09_08/medium/retrain_cutonChi2/${ERA}/${CHANNEL}/nmssm_${CHANNEL}_${MASS}_${MASS_H2}_cmb.json" 

                done

                python merge_json.py --input $IN_JSON --output limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json

                compare_limits.py  ../retrain_uncorrUnc/limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json:exp0:Title='Inclusive',LineStyle=1,LineWidth=2,LineColor=46,MarkerSize=0 limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json:exp0:Title='cut',LineStyle=1,LineWidth=2,LineColor=8,MarkerSize=0 --cms-sub "Own Work" --title-right "$ERA_STRING"  --y-axis-min 0.0001 --y-axis-max 200.0 --show exp   --output plots/limits/${ERA}/${CHANNEL}/nmssm_${ERA}_${CHANNEL}_compare_${MASS} --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 2800.0  --logx  #--draw-theory 

                plotMSSMLimits.py limit_jsons/nmssm_${ERA}_${CHANNEL}_${MASS}_cmb.json --cms-sub "Own Work" --title-right "$ERA_STRING"  --y-axis-min 0.0001 --y-axis-max 500.0  --show exp  --output plots/limits/${ERA}/${CHANNEL}/nmssm_${ERA}_${CHANNEL}_${MASS}_cutonChi2 --logy --process "nmssm" --title-left ${CHANNEL}"   m_{H} = "${MASS}" GeV" --xmax 2800.0  --logx 
        fi
        done

    fi
    
fi
