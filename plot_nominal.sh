ERA=$1
CHANNEL=$2
VARIABLE=$3
for CHANNEL in mt et tt
do
for VARIABLE in m_ttvisbb m_ttbb m_ttbb_puppi  #diBJetPt diBJetEta diBJetPhi diBJetMass diBJetDeltaPhi diBJetAbsDeltaEta diBJetdiLepPhi pt_ttvisbb pt_ttbb pt_ttbb_puppi m_ttvisbb m_ttbb m_ttbb_puppi
 
do

./shapes/produce_shapes_variables_nominal.sh $ERA $CHANNEL $VARIABLE &
done
wait
for VARIABLE in m_ttvisbb m_ttbb m_ttbb_puppi  #diBJetPt diBJetEta diBJetPhi diBJetMass diBJetDeltaPhi diBJetAbsDeltaEta diBJetdiLepPhi pt_ttvisbb pt_ttbb pt_ttbb_puppi m_ttvisbb m_ttbb m_ttbb_puppi

do
#python plot_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_shapes.root -c $CHANNEL --emb --comparison &
#python plot_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_shapes.root -c $CHANNEL --emb  &
python plot_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_shapes.root -c $CHANNEL --emb --ff &
done

done



for CHANNEL in em
do
for VARIABLE in m_ttvisbb m_ttbb m_ttbb_puppi #diBJetPt diBJetEta diBJetPhi diBJetMass diBJetDeltaPhi diBJetAbsDeltaEta diBJetdiLepPhi pt_ttvisbb pt_ttbb pt_ttbb_puppi m_ttvisbb m_ttbb m_ttbb_puppi
do
./shapes/produce_shapes_variables_nominal.sh $ERA $CHANNEL $VARIABLE &
done
wait
for VARIABLE in m_ttvisbb m_ttbb m_ttbb_puppi  #diBJetPt diBJetEta diBJetPhi diBJetMass diBJetDeltaPhi diBJetAbsDeltaEta diBJetdiLepPhi pt_ttvisbb pt_ttbb pt_ttbb_puppi m_ttvisbb m_ttbb m_ttbb_puppi
 
do
#python plot_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_shapes.root -c $CHANNEL --emb --comparison &
#python plot_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_shapes.root -c $CHANNEL --emb  &
python plot_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_shapes.root -c $CHANNEL --emb &
done
wait
done

