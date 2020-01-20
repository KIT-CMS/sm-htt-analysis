#!/bin/bash
oldfolder=$1 # A folder with a dataset_config.yaml that you want to use
newfolder=$2 # Name of the new folder the training goes into.

for era in "2016" "2017" "2018"; do
  for channel in "em" "et" "mt" "tt"; do
    mldir=output/ml/${era}_${channel}_${newfolder}
    olddir=output/ml/${era}_${channel}_${oldfolder}
    mkdir $mldir -p
    ls $mldir
    # Change output path of dataset_config.yaml and copy it into the new folder
    sed "s@output_path: $olddir@output_path: $mldir@" $olddir/dataset_config.yaml > $mldir/dataset_config.yaml
    echo "Created folder $mldir"
  done
done
