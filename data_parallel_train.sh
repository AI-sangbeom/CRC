#!/usr/bin/env bash

PYTHON=${PYTHON:-"python"}
CONFIG=$1
GPUS=$2 

CUDA_VISIBLE_DEVICES=0,1 $PYTHON main/train.py --cfg $CONFIG ${@:3}
