ERA=$1
CHANNEL=$2
VARIABLE=$3

EMBEDDING=1
FAKEFACTOR=1

#./shapes/produce_shapes_variables.sh $ERA $CHANNEL $VARIABLE
./shapes/convert_to_synced_variable_shapes.sh $ERA $CHANNEL $VARIABLE  
./datacards/produce_datacard_variables.sh $ERA stxs_stage0 gof inclusive $EMBEDDING $FAKEFACTOR  $VARIABLE $CHANNEL 
./combine/prefit_shapes.sh $ERA
./plotting/plot_shapes_variables.sh $ERA $VARIABLE gof $EMBEDDING $FAKEFACTOR $CHANNEL


