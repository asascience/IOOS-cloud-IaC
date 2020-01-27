#!/usr/bin/env python3
import os
import multiprocessing as mp
from dask.distributed import Client

# keep things cloud platform agnostic at this layer

# 3rd party dependencies
from prefect import Flow

# Local dependencies
import workflow_tasks as tasks


# Change the following for specific configurations and jobs
#provider = 'Local'
provider = 'AWS'

if provider == 'AWS':
  #fcstconf = 'configs/liveocean.config'
  #fcstjobfile = 'jobs/20191106.liveocean.job'
  fcstconf = 'configs/adnoc.config'
  fcstjobfile = 'jobs/adnoc.job'
  postconf = 'configs/post.config'
  postjobfile = 'jobs/lo.plots.job'

elif provider == 'Local':
  fcstconf = 'configs/local.config'
  fcstjobfile = 'jobs/liveocean.job'
  postconf = 'configs/local.post'
  postjobfile = 'jobs/plots.local.job'


# This is used for obtaining liveocean forcing data
sshuser='ptripp@boiler.ocean.washington.edu'

with Flow('ofs workflow') as flow:
 
  #####################################################################
  # Build Model
  #####################################################################

  #####################################################################
  # Pre-Process
  #####################################################################

  # Get forcing data
  # TODO: make sshuser a Job parameter
  #forcing = tasks.get_forcing(fcstjobfile,sshuser)

  #####################################################################
  # FORECAST
  #####################################################################

  # Create the cluster object
  cluster = tasks.init_cluster(fcstconf,provider)

  # Start the cluster
  fcStarted = tasks.start_cluster(cluster)

  # Setup the job 
  fcstjob = tasks.job_init(cluster, fcstjobfile, 'roms')
  flow.add_edge(fcStarted,fcstjob)

  # Run the forecast
  fcstStatus = tasks.forecast_run(cluster,fcstjob)
  flow.add_edge(fcstjob,fcstStatus)

  # Terminate the cluster nodes
  fcTerminated = tasks.terminate_cluster(cluster)
  flow.add_edge(fcstStatus,fcTerminated)


  #####################################################################
  # Post-Process
  #####################################################################

#######################################################################




def main():

 
  # Potential fix for Mac OS, fixed one thing but still wont run
  #mp.set_start_method('spawn')
  #mp.set_start_method('forkserver')

  # matplotlib Mac OS issues
  flow.run()

#######################################################################

 
if __name__ == '__main__':
  main()
