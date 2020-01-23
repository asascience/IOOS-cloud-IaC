#!/usr/bin/env python3
import os
import multiprocessing as mp
from dask.distributed import Client

# keep things cloud platform agnostic at this layer

# 3rd party dependencies
from prefect import Flow

# Local dependencies
import workflow_tasks as tasks


# Set these
#fcstconf = 'configs/test.config'
fcstconf = 'configs/liveocean.config'
postconf = 'configs/local.post'
#fcstjobfile = 'jobs/liveocean.job'
fcstjobfile = 'jobs/20191106.liveocean.job'
#postjobfile = 'jobs/plots.local.job'
postjobfile = 'jobs/lo.plots.job'

# This is used for obtaining liveocean forcing data
sshuser='ptripp@boiler.ocean.washington.edu'

#with Flow('test') as testflow:
  #forcing = tasks.get_forcing(fcstjobfile,sshuser)


with Flow('plot only') as plotonly:


  # Start a machine
  postmach = tasks.init_cluster(postconf,'Local')
  pmStarted = tasks.start_cluster(postmach)

  # Push the env, install required libs on post machine
  # TODO: install all of the 3rd party dependencies on AMI
  #pushPy = tasks.push_pyEnv(postmach, upstream_tasks=[pmStarted])

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

  pmTerminated = tasks.terminate_cluster(postmach,upstream_tasks=[plots,closedask])

  
  #pmTerminated = tasks.terminate_cluster(postmach,upstream_tasks=[FILES])
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
  cluster = tasks.init_cluster(fcstconf,'Local')

  # Start the cluster
  fcStarted = tasks.start_cluster(cluster)

  # Setup the job 
  # TODO: Template this in npzd2o_Banas.in or copy the rivers.nc file over
  #   SSFNAME == /com/liveocean/forcing/f2019.11.06/riv2/rivers.nc
  fcstjob = tasks.job_init(cluster, fcstjobfile, 'roms')

  # Run the forecast
  fcstStatus = tasks.forecast_run(cluster,fcstjob)

  # Terminate the cluster nodes
  fcTerminated = tasks.terminate_cluster(cluster)

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
  postmach = tasks.init_cluster(postconf,'Local')
  pmStarted = tasks.start_cluster(postmach, upstream_tasks=[fcstStatus])

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

  pmTerminated = tasks.terminate_cluster(postmach,upstream_tasks=[plots])

#####################################################################



def main():

 
  # Potential fix for Mac OS, fixed one thing but still wont run
  #mp.set_start_method('spawn')
  #mp.set_start_method('forkserver')

  # matplotlib Mac OS issues
  #flow.run()
  #testflow.run()
  plotonly.run()

#####################################################################

 
if __name__ == '__main__':
  main()
