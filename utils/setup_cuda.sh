#!/bin/bash

export PATH=/usr/local/cuda-10.0/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-10.0/lib64:$LD_LIBRARY_PATH

#Selects GPU with the least used Memory
export CUDA_VISIBLE_DEVICES=$( nvidia-smi | grep 250W | egrep -o '[0-9]+MiB /' | egrep -o '[0-9]+' | awk '{print NR-1 " " $0}' | sort -g -k 2n | head -c 2)

export PYTHONUSERBASE=$HOME/.local/pylibs-$(hostname)
export PYTHONPATH=$HOME/.local/pylibs-$(hostname)/lib/python2.7/site-packages:$PYTHONPATH
export PATH=$HOME/.local/pylibs-$(hostname)/bin:$PATH
