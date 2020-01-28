#!/usr/bin/env python3
import os
import multiprocessing as mp
from dask.distributed import Client

# keep things cloud platform agnostic at this layer

# 3rd party dependencies
from prefect import Flow

# Local dependencies
import workflow_tasks as tasks


# Set these for specific use

provider = 'Local'
#provider = 'AWS'

if provider == 'AWS':
  fcstconf = 'configs/liveocean.config'
  fcstjobfile = 'jobs/20191106.liveocean.job'
  postconf = 'configs/post.config'
  postjobfile = 'jobs/lo.plots.job'

elif provider == 'Local':
  fcstconf = 'configs/local.config'
  fcstjobfile = 'jobs/liveocean.job'
  postconf = 'configs/local.post'
  postjobfile = 'jobs/plots.local.job'


# This is used for obtaining liveocean forcing data
sshuser='ptripp@boiler.ocean.washington.edu'


with Flow('plot only') as plotonly:

  # Start a machine
  postmach = tasks.cluster_init(postconf,provider)
  pmStarted = tasks.cluster_start(postmach)

  # Push the env, install required libs on post machine
  # TODO: install all of the 3rd party dependencies on AMI
  pushPy = tasks.push_pyEnv(postmach, upstream_tasks=[pmStarted])

  # Start a dask scheduler on the new post machine
  daskclient : Client = tasks.start_dask(postmach, upstream_tasks=[pmStarted])

  # Setup the post job
  postjob = tasks.job_init(postmach, postjobfile, 'plotting', upstream_tasks=[pmStarted])

  # Get list of files from fcstjob
  FILES = tasks.ncfiles_from_Job(postjob)

  # Make plots
  plots = tasks.daskmake_plots(daskclient, FILES, postjob)
  plots.set_upstream([daskclient])

  closedask = tasks.dask_client_close(daskclient, upstream_tasks=[plots])
  pmTerminated = tasks.cluster_terminate(postmach,upstream_tasks=[plots,closedask])

#######################################################################




with Flow('ofs workflow') as flow:


  #####################################################################
  # Pre-Process
  #####################################################################

  # Get forcing data
  #forcing = tasks.get_forcing(fcstjobfile,sshuser)


  #####################################################################
  # FORECAST
  #####################################################################

  # Create the cluster object
  cluster = tasks.cluster_init(fcstconf,'AWS')

  # Start the cluster
  fcStarted = tasks.cluster_start(cluster)

  # Setup the job 
  fcstjob = tasks.job_init(cluster, fcstjobfile, 'roms')

  # Run the forecast
  fcstStatus = tasks.forecast_run(cluster,fcstjob)

  # Terminate the cluster nodes
  fcTerminated = tasks.cluster_terminate(cluster)

  flow.add_edge(fcStarted,fcstjob)
  flow.add_edge(fcstjob,fcstStatus)
  flow.add_edge(fcstStatus,fcTerminated)


  #####################################################################
  # POST Processing
  #####################################################################
  # Spin up a new machine?
  # or launch a container?
  # or run concurrently on the forecast cluster?
  # or run on the local machine? concurrrently? 

  # Start a machine
  postmach = tasks.cluster_init(postconf,provider)
  pmStarted = tasks.cluster_start(postmach, upstream_tasks=[fcstStatus])

  # Push the env, install required libs on post machine
  # TODO: install all of the 3rd party dependencies on AMI
  pushPy = tasks.push_pyEnv(postmach, upstream_tasks=[pmStarted])

  # Start a dask scheduler on the new post machine
  daskclient = tasks.start_dask(postmach, upstream_tasks=[pushPy])

  # Setup the post job
  postjob = tasks.job_init(postmach, postjobfile, 'plotting', upstream_tasks=[pmStarted])

  # Get list of files from fcstjob
  FILES = tasks.ncfiles_from_Job(postjob, upstream_tasks=[fcstStatus])

  # Make plots
  plots = tasks.daskmake_plots(daskclient, FILES, postjob)
  plots.set_upstream([daskclient])

  closedask = tasks.dask_client_close(daskclient, upstream_tasks=[plots])
  pmTerminated = tasks.cluster_terminate(postmach,upstream_tasks=[plots,closedask])

#####################################################################



def main():

 
  # Potential fix for Mac OS, fixed one thing but still wont run
  #mp.set_start_method('spawn')
  #mp.set_start_method('forkserver')

  # matplotlib Mac OS issues
  #flow.run()
  #testflow.run()
  #plotonly.run()

#####################################################################

 
if __name__ == '__main__':
  main()