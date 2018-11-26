#!/bin/bash

ERAS=${@}

# Clean any existing files
rm -rf output/combined_smhtt

# Make new directory with needed folder structure
mkdir -p output/combined_smhtt/cmb/125
mkdir -p output/combined_smhtt/cmb/common

# Copy files of each era in these folders
for ERA in $ERAS
do
    cp output/${ERA}_smhtt/cmb/125/htt_*_Run${ERA}.txt output/combined_smhtt/cmb/125/
    cp output/${ERA}_smhtt/cmb/common/htt_input_Run${ERA}.root output/combined_smhtt/cmb/common/
done
