#!/usr/bin/env python3
import os
import sys
import multiprocessing as mp
from dask.distributed import Client

# keep things cloud platform agnostic at this layer

# 3rd party dependencies
from prefect import Flow

# Local dependencies
import workflow_tasks as tasks

# Set these for specific use

#provider = 'Local'
provider = 'AWS'

if provider == 'AWS':
  fcstconf = 'configs/liveocean.config'
  fcstjobfile = 'jobs/liveocean.job'
  postconf = 'configs/post.config'
  postjobfile = 'jobs/liveocean.plots.job'

elif provider == 'Local':
  fcstconf = 'configs/local.config'
  fcstjobfile = 'jobs/liveocean.job'
  postconf = 'configs/local.post'
  postjobfile = 'jobs/plots.local.job'


# This is used for obtaining liveocean forcing data
# Users other than ptripp will need to obtain credentials from UW
sshuser='ptripp@boiler.ocean.washington.edu'


with Flow('test mpeg') as testmpeg:
  postmach = tasks.cluster_init(postconf,provider)
  plotjob = tasks.job_init(postmach, postjobfile, 'plotting')
  mpegs = tasks.make_mpegs(plotjob)

  storage_service = tasks.storage_init(provider)
  savetocloud = tasks.save_to_cloud(plotjob, storage_service, ['*.mp4'], public=True)
  savetocloud.set_upstream(mpegs)


with Flow('test forcing') as testforce:
  # Get forcing data
  forcing = tasks.get_forcing(fcstjobfile,sshuser)


with Flow('fcst workflow') as fcstflow:

  #####################################################################
  # Pre-Process
  #####################################################################

  # Get forcing data
  forcing = tasks.get_forcing(fcstjobfile,sshuser)


  #####################################################################
  # FORECAST
  #####################################################################

  # Create the cluster object
  cluster = tasks.cluster_init(fcstconf,provider)

  # Start the cluster
  fcStarted = tasks.cluster_start(cluster)

  # Setup the job 
  fcstjob = tasks.job_init(cluster, fcstjobfile, 'roms')

  # Run the forecast
  fcstStatus = tasks.forecast_run(cluster,fcstjob)

  # Terminate the cluster nodes
  fcTerminated = tasks.cluster_terminate(cluster)

  fcstflow.add_edge(fcStarted,fcstjob)
  fcstflow.add_edge(fcstjob,fcstStatus)
  fcstflow.add_edge(fcstStatus,fcTerminated)

#####################################################################



with Flow('plotting') as plotflow:

  #####################################################################
  # POST Processing
  #####################################################################

  # Start a machine
  postmach = tasks.cluster_init(postconf,provider)
  pmStarted = tasks.cluster_start(postmach)

  # Push the env, install required libs on post machine
  # TODO: install all of the 3rd party dependencies on AMI
  pushPy = tasks.push_pyEnv(postmach, upstream_tasks=[pmStarted])

  # Start a dask scheduler on the new post machine
  daskclient : Client = tasks.start_dask(postmach, upstream_tasks=[pmStarted])

  # Setup the post job
  plotjob = tasks.job_init(postmach, postjobfile, 'plotting', upstream_tasks=[pmStarted])

  # Get list of files from job specified directory
  FILES = tasks.ncfiles_from_Job(plotjob,"ocean_his_*.nc")

  # Make plots
  #plots = tasks.daskmake_plots(daskclient, FILES, plotjob)
  #plots.set_upstream([daskclient])

  storage_service = tasks.storage_init(provider)
  #pngtocloud = tasks.save_to_cloud(plotjob, storage_service, ['*.png'], public=True)
  #pngtocloud.set_upstream(plots)

  # Make movies
  #mpegs = tasks.daskmake_mpegs(plotjob, upstream_tasks=[plots])
  mpegs = tasks.daskmake_mpegs(daskclient, plotjob, upstream_tasks=[daskclient])
  mp4tocloud = tasks.save_to_cloud(plotjob, storage_service, ['*.mp4'], public=True)
  mp4tocloud.set_upstream(mpegs)

  closedask = tasks.dask_client_close(daskclient, upstream_tasks=[mpegs])
  pmTerminated = tasks.cluster_terminate(postmach,upstream_tasks=[mpegs,closedask])

#######################################################################


def main():
  # matplotlib Mac OS issues
  # Potential fix for Mac OS, fixed one thing but still wont run
  #mp.set_start_method('spawn')
  #mp.set_start_method('forkserver')
  #plotstate = plotflow.run()

  test()
  sys.exit()
  
  fcststate = fcstflow.run()
  if fcststate.is_successful():
    plotstate = plotflow.run()

#####################################################################

def test():
  plotstate = plotflow.run()
  #testmpeg.run()

 
if __name__ == '__main__':
  main()
