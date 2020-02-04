#!/bin/bash

cd $HOME/IOOS-cloud-IaC/python

job1=jobs/liveocean.qops.job
job2=jobs/liveocean.qops.plots.job

workflows/liveocean_qops.py $job1 $job2 > $HOME/lo.log 2>&1
