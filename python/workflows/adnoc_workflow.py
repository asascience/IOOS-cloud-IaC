#!/usr/bin/env python3

# keep things cloud platform agnostic at this layer

# Local dependencies
import workflow_tasks as tasks
# 3rd party dependencies
from prefect import Flow

# Change the following for specific configurations and jobs
#provider = 'Local'
provider = 'AWS'

fcstconf = ""
fcstjobfile = ""

if provider == 'AWS':
  fcstconf = 'configs/adnoc.config'
  fcstjobfile = 'jobs/adnoc.job'
elif provider == 'Local':
  fcstconf = 'configs/local.config'
  fcstjobfile = 'jobs/adnoc.job'


with Flow('ofs workflow') as flow:

  #####################################################################
  # FORECAST
  #####################################################################

  # Create the cluster object
  cluster = tasks.cluster_init(fcstconf,provider)

  # Start the cluster
  fcStarted = tasks.cluster_start(cluster)

  # Setup the job 
  fcstjob = tasks.job_init(cluster, fcstjobfile, 'roms')
  flow.add_edge(fcStarted,fcstjob)

  # Run the forecast
  fcstStatus = tasks.forecast_run(cluster,fcstjob)
  flow.add_edge(fcstjob,fcstStatus)

  # Terminate the cluster nodes
  fcTerminated = tasks.cluster_terminate(cluster)
  flow.add_edge(fcstStatus,fcTerminated)

#######################################################################


def main():
  flow.run()

if __name__ == '__main__':
  main()
