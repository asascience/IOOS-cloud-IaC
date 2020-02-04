#!/usr/bin/env python3
import os
import sys
import collections
import multiprocessing as mp


# keep things cloud platform agnostic at this layer

# 3rd party dependencies
from prefect import Flow
from dask.distributed import Client

# Local dependencies
import workflow_tasks as tasks
import romsUtil as util
import flows

# Set these for specific use
curdir = os.path.dirname(os.path.abspath(__file__))

#provider = 'Local'
provider = 'AWS'
fcstconf = f'{curdir}/../configs/liveocean.config'
postconf = f'{curdir}/../configs/post.config'

# This is used for obtaining liveocean forcing data
# Users other than ptripp will need to obtain credentials from UW
sshuser='ptripp@boiler.ocean.washington.edu'


def main():

  lenargs = len(sys.argv) - 1
  print(f"lenargs: {lenargs}")

  joblist = []

  idx = 1
  while idx <= lenargs:
    print(f"sys.argv[{idx}] : {sys.argv[idx]}")
    ajobfile = os.path.abspath(sys.argv[idx])
    joblist.append(ajobfile)
    idx += 1

  flowdeq = collections.deque()

  for jobfile in joblist:
    jobdict = util.readConfig(jobfile)
    jobtype = jobdict['JOBTYPE']
    print('JOBTYPE: ',jobtype)

    # Add the forecast flow
    if jobtype == 'forecast':
      fcstflow = flows.fcst_flow(fcstconf, jobfile)
      flowdeq.appendleft(fcstflow)

    # Add the plot flow
    elif jobtype == 'plotting':
      postjobfile = jobfile
      plotflow = flows.plot_flow(postconf, jobfile)
      flowdeq.appendleft(plotflow)

    else:
      print(f"jobtype: {jobtype} is not supported")
      sys.exit()
 
  qlen = len(flowdeq) 
  idx = 0

  while idx < qlen:
    aflow = flowdeq.pop()
    idx += 1 
    state = aflow.run()
    if state.is_successful(): continue
    else: break
        

#####################################################################

 
if __name__ == '__main__':
  main()
