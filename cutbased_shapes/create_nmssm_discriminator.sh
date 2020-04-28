#!/bin/bash

source utils/setup_cvmfs_sft.sh

ERA=$1
CHANNEL=$2
VARIABLE=$3

python cutbased_shapes/create_nmssm_discriminator.py --cores 1 --variable ${VARIABLE}  --inputs output/shapes/${ERA}_${CHANNEL}_m_ttvisbb_cutbased_shapes_m_ttvisbb.root output/shapes/${ERA}_${CHANNEL}_mbb_cutbased_shapes_mbb.root output/shapes/${ERA}_${CHANNEL}_m_sv_puppi_cutbased_shapes_m_sv_puppi.root



