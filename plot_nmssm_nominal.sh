ERA=$1
CHANNEL=$2
VARIABLE=$3

for CHANNEL in mt et tt em
do
for VARIABLE in nbtag #m_sv_puppi m_ttvisbb pt_bb mbb  m_ttbb_puppi #nmssm_discriminator
do
#./cutbased_shapes/produce_shapes_variables_nominal.sh $ERA $CHANNEL m_vis &
#./cutbased_shapes/produce_shapes_variables_nominal.sh $ERA $CHANNEL mbb &
#./cutbased_shapes/produce_shapes_variables_nominal.sh $ERA $CHANNEL m_ttvisbb &
echo "1"
./cutbased_shapes/produce_shapes_variables_nominal.sh $ERA $CHANNEL $VARIABLE &
#python cutbased_shapes/create_nmssm_discriminator.py --cores 1 --variable ${VARIABLE}  --inputs output/shapes/nominal/${ERA}_${CHANNEL}_m_ttvisbb_cutbased_shapes_m_ttvisbb.root output/shapes/nominal/${ERA}_${CHANNEL}_mbb_cutbased_shapes_mbb.root output/shapes/nominal/${ERA}_${CHANNEL}_m_sv_puppi_cutbased_shapes_m_sv_puppi.root
done
done
wait

for CHANNEL in mt et tt em
do
for VARIABLE in nbtag #m_sv_puppi  m_ttvisbb pt_bb mbb m_ttbb_puppi
do
for CATEGORY in inclusive #1btag 2btag 1btag_boosted 1btag_background 1btag_signal_unboosted 2btag_boosted 2btag_background 2btag_signal_unboosted 
do
        # python plot_nmssm_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_cutbased_shapes_${VARIABLE}.root 
        # python plot_nmssm_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_cutbased_shapes_${VARIABLE}.root -c $CHANNEL --emb  &
        # python plot_nmssm_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_cutbased_shapes_${VARIABLE}.root -c $CHANNEL --ff  &
        python plot_nmssm_nominal.py  -v ${VARIABLE} --era Run${ERA}  --shapes output/shapes/nominal/${ERA}_${CHANNEL}_${VARIABLE}_cutbased_shapes_${VARIABLE}.root -c $CHANNEL --emb  --blind  --x-log --categories ${CHANNEL}_${CATEGORY} --output-dir plots/blinded/xlog --ff  &
        python plot_nmssm_nominal.py  -v ${VARIABLE} --era Run${ERA}  --shapes output/shapes/nominal/${ERA}_${CHANNEL}_${VARIABLE}_cutbased_shapes_${VARIABLE}.root -c $CHANNEL --emb  --blind   --categories ${CHANNEL}_${CATEGORY} --output-dir plots/blinded/nolog --ff  &
        python plot_nmssm_nominal.py  -v ${VARIABLE} --era Run${ERA}  --shapes output/shapes/nominal/${ERA}_${CHANNEL}_${VARIABLE}_cutbased_shapes_${VARIABLE}.root -c $CHANNEL --emb  --x-log --categories ${CHANNEL}_${CATEGORY} --output-dir plots/unblinded/xlog --ff &
        python plot_nmssm_nominal.py  -v ${VARIABLE} --era Run${ERA}  --shapes output/shapes/nominal/${ERA}_${CHANNEL}_${VARIABLE}_cutbased_shapes_${VARIABLE}.root -c $CHANNEL --emb   --categories ${CHANNEL}_${CATEGORY} --output-dir plots/unblinded/nolog --ff  &
done

done
done
wait






