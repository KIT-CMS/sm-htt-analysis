ERA=$1
CHANNEL=$2
VARIABLE=$3
for CHANNEL in em
do
        for VARIABLE in mbb m_ttvisbb m_ttbb m_ttbb_puppi pt_bb bdeta m_vis
        do
	echo "1"
        ./cutbased_shapes/produce_shapes_variables_nominal.sh $ERA $CHANNEL $VARIABLE &
        done
    wait 
    
    for CATEGORY in 1btag 2btag 
    do
        for VARIABLE in mbb m_ttvisbb m_ttbb m_ttbb_puppi pt_bb bdeta m_vis
        do
        # python plot_nmssm_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_cutbased_shapes_${VARIABLE}.root 
        # python plot_nmssm_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_cutbased_shapes_${VARIABLE}.root -c $CHANNEL --emb  &
        # python plot_nmssm_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_cutbased_shapes_${VARIABLE}.root -c $CHANNEL --ff  &
        python plot_nmssm_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_cutbased_shapes_${VARIABLE}.root -c $CHANNEL --emb --categories ${CHANNEL}_${CATEGORY}  &
        done
    done
    wait
done

