#!/bin/bash
#Written by ml_condor/write_condor_submission.sh
#Called by condor container as startup following job request from ml_condor/setup_condor_training.sh
ERA=all_eras
CHANNEL=tt
TAG=500_2
./run_condor_training_gpu.sh all_eras tt 500_2
