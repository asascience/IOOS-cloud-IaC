#!/usr/bin/env python3
import os

# keep things cloud platform agnostic at this layer

# 3rd party dependencies
from prefect import Flow
#from dask.distributed import Client

# Local dependencies
import workflow_tasks as tasks



#######################################################################
 # Customize
with Flow('ofs workflow') as flow:

  #####################################################################
  # FORECAST
  #####################################################################

  # Create the cluster object
  config='./configs/test.config'
  #config='./configs/liveocean.config'
  cluster = tasks.init_cluster(config)

  # Start the cluster
  fcStarted = tasks.start_cluster(cluster)

  # Setup the job 
  jobDesc = "jobs/liveocean.job"
  job = tasks.job_init(cluster, jobDesc)

  # Run the forecast
  # TODO: fix return value from this, is reporting success when failed
  fcstStatus = tasks.forecast_run(cluster,job)

  # Terminate the cluster nodes
  fcTerminated = tasks.terminate_cluster(cluster)

  flow.add_edge(fcStarted,job)
  flow.add_edge(job,fcstStatus)
  flow.add_edge(fcstStatus,fcTerminated)


  #####################################################################
  # POST Processing
  #####################################################################
  # Spin up a new machine?
  # or launch a container?
  # or run concurrently on above?
  # or run on local machine?

  # COMOUT is set in job_init task
  #  but prefect is getting in the way of accessing it here
  # TODO: Make a new task to wrap this, return FILES list
  # Post job should contain this info
  # TODO: Finish Job class
  COMOUT = '/com/liveocean/current'
  SOURCE = os.path.abspath(f"{COMOUT}")
  TARGET = os.path.abspath(f"{COMOUT}/plots")
  FILES = tasks.ncfiles_glob(SOURCE, upstream_tasks=[fcstStatus])

  # Start a machine
  postconfig = './configs/post.config'
  postmach = tasks.init_cluster(postconfig)
  pmStarted = tasks.start_cluster(postmach, upstream_tasks=[fcstStatus])

  # Push the env, install required libs on post machine
  # TODO: install all of the 3rd party dependencies on AMI
  pushPy = tasks.push_pyEnv(postmach, upstream_tasks=[pmStarted])

  # Start a dask scheduler on the host
  daskclient = tasks.start_dask(postmach, upstream_tasks=[pushPy])

  # Make plots
  plots = tasks.daskmake_plots(daskclient, FILES, TARGET, 'temp')
  plots.set_upstream([daskclient])

  pmTerminated = tasks.terminate_cluster(postmach,upstream_tasks=[plots])


#####################################################################

def main():

  jobDesc = "jobs/liveocean.job"

  print(flow.tasks)

  flow.run()

#####################################################################

 
if __name__ == '__main__':
  main()
