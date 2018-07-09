#!/bin/bash

# Error handling to ensure that script is executed from top-level directory of
# this repository
for DIRECTORY in shapes datacards combine plotting utils
do
    if [ ! -d "$DIRECTORY" ]; then
        echo "[FATAL] Directory $DIRECTORY not found, you are not in the top-level directory of the analysis repository?"
        exit 1
    fi
done

## Clean-up workspace
./utils/clean.sh

# create histograms for all variables; m_nn, pt_nn etc.
# in bins of jet multiplicity
#CHANNELS="tt mt et"
CHANNELS="tt mt"
#CATEGORIES="inclusive 0jet 1jet 2jet"
CATEGORIES="inclusive"
#VARIABLES="m_nn m_sv pt_nn pt_sv eta_nn eta_sv phi_nn phi_sv pt_nt_1 phi_nt_1 m_nt_1 pt_nt_2 phi_nt_2 m_nt_2 e_nt_1 e_nt_2 px_nt_1 py_nt_1 pz_nt_1 px_nt_2 py_nt_2 pz_nt_2"
#VARIABLES="pt_nt_1 m_nt_1 pt_nt_2 m_nt_2 eta_nt_1 eta_nt_2" 
VARIABLES="m_N m_sv pt_N pt_sv eta_N eta_sv phi_N phi_sv" #pt_nt_1 pt_nt_2  eta_nt_1 eta_nt_2 e_nt_1 e_nt_2" 
./shapes/produce_shapes.sh --channels $CHANNELS --categories $CATEGORIES --variables $VARIABLES

# create plots from them

python Dumbledraw/plot_variable.py --channels $CHANNELS --categories $CATEGORIES --variables $VARIABLES
