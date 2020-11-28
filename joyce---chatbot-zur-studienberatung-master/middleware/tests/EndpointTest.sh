#!/bin/bash


ENV_NAME=$(grep -o '"env_name": "[^"]*' ../config/config.json | grep -o '[^"]*$')
conda activate $ENV_NAME
python ../main.py &
