#!/bin/bash

source utils/setup_cvmfs_sft.sh

echo "Sourced python executable:" `which python`

pip install --user --upgrade sklearn
