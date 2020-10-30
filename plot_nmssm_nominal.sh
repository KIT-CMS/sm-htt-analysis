ERA=$1
CHANNEL=$2
VARIABLE=$3
#for VARIABLE in  mjj pt_1 pt_2 m_vis ptvis m_sv_puppi jpt_1 njets jdeta mjj dijetpt bpt_bReg_1 bpt_bReg_2 jpt_2 mbb_highCSV_bReg pt_bb_highCSV_bReg m_ttvisbb_highCSV_bReg kinfit_mH kinfit_mh2 kinfit_chi2 nbtag  bm_bReg_1 bm_bReg_2 bcsv_1 bcsv_2 highCSVjetUsedFordiBJetSystemCSV
#do

./shapes/produce_shapes_variables_nominal.sh $ERA $CHANNEL $VARIABLE 

python plot_nmssm_nominal.py  -v ${VARIABLE} --era Run${ERA}  --shapes output/shapes/${ERA}_${CHANNEL}_${VARIABLE}/${ERA}-${ERA}_${CHANNEL}_${VARIABLE}-${CHANNEL}-shapes.root -c $CHANNEL --emb   --output-dir plots/hiscore/nolog --ff

#done



