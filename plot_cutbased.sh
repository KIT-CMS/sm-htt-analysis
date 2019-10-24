ERA=$1
CHANNEL=$2
VARIABLE=$3
for CHANNEL in et mt tt
do 
for VARIABLE in diBJetMass 
do
python plot_cutbased.py  -v $VARIABLE --categories ${CHANNEL}_signal_unboosted --era Run${ERA}  --shapes 2017_cutbased_shapes_diBJetMass.root  -c $CHANNEL --emb --ff --blind &
python plot_cutbased.py  -v $VARIABLE --categories ${CHANNEL}_boosted --era Run${ERA}  --shapes 2017_cutbased_shapes_diBJetMass.root  -c $CHANNEL --emb --ff --blind &
python plot_cutbased.py  -v $VARIABLE --categories ${CHANNEL}_background --era Run${ERA}  --shapes 2017_cutbased_shapes_diBJetMass.root  -c $CHANNEL --emb --ff &

done
done
wait
