#!/bin/bash

source utils/setup_cvmfs_sft.sh

hadd -f 2017_cutbased_shapes_diBJetMass.root 2017_??_*_cutbased_shapes_diBJetMass.root
python fake-factor-application/normalize_shifts.py 2017_cutbased_shapes_diBJetMass.root

./cutbased_shapes/convert_to_synced_shapes.sh 2017 diBJetMass