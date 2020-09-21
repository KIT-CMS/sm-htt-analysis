ERA=$1
CHANNEL=$2
VARIABLE=$3
MODE=$4



if [ "$MODE" == "prefit" ]; then
for ERA in  2016 2017 2018
do
for CHANNEL in  tt mt et

do

python add_hists.py CMSSW_10_2_16_UL/src/output_${ERA}_${CHANNEL}_nmssm_500_100/${ERA}/cmb/prefitshape.root --input-hist ggH125 ttH125 qqH125 --output-hist HTT 


python plot_nmssm_nominal.py  -v ${VARIABLE} --era Run${ERA}  -c $CHANNEL --emb   --output-dir plots/prefit --ff --prefit --shapes CMSSW_10_2_16_UL/src/output_${ERA}_${CHANNEL}_nmssm_500_100/${ERA}/cmb/prefitshape.root 
# python plot_nmssm_nominal.py  -v ${VARIABLE} --era Run${ERA}  -c $CHANNEL --emb   --output-dir plots/fit --ff --prefit --shapes CMSSW_10_2_16_UL/src/output_${ERA}_${CHANNEL}_nmssm_500_100/${ERA}/cmb/postfitshape.root &
done
done 
wait
else


for ERA in 2018 2016 2017
do
for CHANNEL in tt mt et
do

for VARIABLE in  mjj pt_1 pt_2 m_vis ptvis m_sv_puppi jpt_1 njets jdeta mjj dijetpt bpt_bReg_1 bpt_bReg_2 jpt_2 mbb_highCSV_bReg pt_bb_highCSV_bReg m_ttvisbb_highCSV_bReg kinfit_mH kinfit_mh2 kinfit_chi2 nbtag  bm_bReg_1 bm_bReg_2 bcsv_1 bcsv_2 highCSVjetUsedFordiBJetSystemCSV
do
./shapes/produce_shapes_variables_nominal.sh $ERA $CHANNEL $VARIABLE & 
echo "1"
done 
wait
done



#for ERA in 2016 2017 2018
#do
for CHANNEL in tt et mt
do


for VARIABLE in  mjj pt_1 pt_2 m_vis ptvis m_sv_puppi jpt_1 njets jdeta mjj dijetpt bpt_bReg_1 bpt_bReg_2 jpt_2 mbb_highCSV_bReg pt_bb_highCSV_bReg m_ttvisbb_highCSV_bReg kinfit_mH kinfit_mh2 kinfit_chi2 nbtag  bm_bReg_1 bm_bReg_2 bcsv_1 bcsv_2 highCSVjetUsedFordiBJetSystemCSV

do

python plot_nmssm_nominal.py  -v ${VARIABLE} --era Run${ERA}  --shapes output/shapes/${ERA}_${CHANNEL}_${VARIABLE}/${ERA}-${ERA}_${CHANNEL}_${VARIABLE}-${CHANNEL}-shapes.root -c $CHANNEL --emb   --output-dir plots/hiscore/nolog --ff &
done

wait

done

done
fi





