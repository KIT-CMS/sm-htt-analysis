#!/bin/bash
#This script runs inside the cluster.
#Written by ml_condor/write_condor_submission.sh
#Called by condor container as startup following job request from ml_condor/setup_condor_training.sh
./run_condor_training_gpu.sh all_eras mt 500_2 tvoigtlaender
