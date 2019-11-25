#!/bin/bash
oldfolder=$1 # A folder with a dataset_config.yaml that you want to use
newfolder=$2 # Name of the new folder the training goes into.

mkdir "output/ml/$newfolder" -p

# Change output path of dataset_config.yaml and copy it into the new folder
sed "s@output_path: output/ml/$oldfolder@output_path: output/ml/$newfolder@" output/ml/$oldfolder/dataset_config.yaml > output/ml/$newfolder/dataset_config.yaml