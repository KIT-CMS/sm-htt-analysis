ERA=$1
CHANNEL="mt"
VARIABLE="m_vis"

cp output/shapes/${ERA}_${CHANNEL}_${VARIABLE}/${ERA}-${ERA}_${CHANNEL}_${VARIABLE}-${CHANNEL}-shapes.root ${ERA}_shapes.root

# Convert to synced shapes
./convert_to_synced_shapes.sh $ERA $CHANNEL $VARIABLE

# Create datacard
JETFAKES=1
EMBEDDING=1
./produce_datacard.sh $ERA $CHANNEL $VARIABLE $JETFAKES $EMBEDDING $VARIABLE
mv output/datacards/cmb/\*  output/datacards/cmb/tauES #yikes

# Create workspace
./produce_workspace.sh $ERA | tee ${ERA}_produce_workspace_inclusive.log

./fit.sh $ERA

./combine/nuisance_impacts.sh $ERA

