#!/usr/bin/env python3

# keep things cloud platform agnostic at this layer
# Python dependencies
import sys
import os
import json
import pprint
import subprocess
import traceback
import glob
from datetime import timedelta

# 3rd party dependencies
from prefect import task, unmapped
from prefect.engine import signals
from prefect.triggers import all_successful, all_finished
from dask.distributed import Client

# Local dependencies
from Cluster.AWSCluster import AWSCluster
from Job import Job
from Job.ROMSForecast import ROMSForecast
from Job.Plotting import Plotting

import romsUtil as util

from plotting.plot import plot_roms

pp = pprint.PrettyPrinter()
debug = False


@task
def init_cluster(config) -> AWSCluster :

  # TODO later: implement AzureCluster
  try:
    cluster = AWSCluster(config)
  except Exception as e:
    print('Could not create cluster: ' + str(e))
    sys.exit()
  return cluster
#######################################################################



@task
def start_cluster(cluster):

  print('Starting ' + str(cluster.nodeCount) + ' instances ...')
  try:
    cluster.start()
  except Exception as e:
    print('In driver: Exception while creating nodes :' + str(e))
    sys.exit()
  return
#######################################################################


@task(trigger=all_finished)
def terminate_cluster(cluster):

  responses = cluster.terminate()
  # Just check the state
  print('Responses from terminate: ')
  for response in responses :
    pp.pprint(response)

  return
#######################################################################




@task
def job_init(cluster, configfile, jobtype) -> Job :

  # We can't really separate the hardware from the job, nprocs is needed
  NPROCS = cluster.nodeCount * cluster.PPN

  # Need to make this a factory
  if jobtype == 'roms':
    job = ROMSForecast(configfile, NPROCS )
  elif jobtype == 'plotting':
    job = Plotting(configfile,NPROCS)
  else:
    print("Unsupported job type")
    raise Exception("unsupported job type : ", jobtype)

  return job
#######################################################################




# TODO, make job class and use object here
@task
def forecast_run(cluster, job):

  PPN = cluster.getCoresPN()

  # Easier to read
  CDATE = job.CDATE
  HH = job.HH
  OFS = job.OFS
  NPROCS = job.NPROCS

  runscript="fcst_launcher.sh"
 
  result = 1
 
  try:
    HOSTS=cluster.getHostsCSV()
  except Exception as e:
    print('In driver: execption retrieving list of hostnames:' + str(e))
    raise signals.FAIL()

  try:
    result = subprocess.run([runscript,CDATE,HH,str(NPROCS),str(PPN),HOSTS,OFS], \
      stderr=subprocess.STDOUT)
  except Exception as e:
    print('In driver: Exception during subprocess.run :' + str(e))
    raise signals.FAIL()


  if result != 0 :
    print('Forecast failed ... result: ', result)
    raise signals.FAIL()

  print('Forecast finished successfully')
  return 
#######################################################################



@task
def ncfiles_glob(SOURCE):
    FILES = sorted(glob.glob(f'{SOURCE}/*.nc'))
    for f in FILES:
      print(f)
    return FILES
#####################################################################


@task
def ncfiles_from_Job(job : Job):
    SOURCE = job.OUTDIR
    return ncfiles_glob(SOURCE)
#####################################################################



@task
def make_plots(filename,target,varname):

  print(f"{filename} {target} {varname}")
  plot_roms(filename,target,varname)
  return
#####################################################################




@task
def daskmake_plots(client: Client, FILES: list, plotjob: Job ):

  target = plotjob.OUTDIR

  # TODO: implement multiple VARS in Job
  varname = plotjob.VARS[0]

  print("In daskmake_plots", FILES)

  if not os.path.exists(target):
      os.mkdir(target)

  idx = 0
  futures = []
  for filename in FILES:
    future = client.submit(plot_roms, filename, target, varname)
    futures.append(future)
    print(futures[idx])
    idx += 1
  
  for future in futures:
    result = future.result()
    print(result)

  # Was unable to get it to work using client.map()
  #filenames = FILES[0:1]
  #print("mapping plot_roms over filenames")
  #futures = client.map(plot_roms, filenames, pure=False, target=unmapped(target), varname=unmapped(varname))
  #print("Futures:",futures)
  # Wait for the processes to finish, gather the results
  #results = client.gather(futures)
  #print("gathered results")
  #print("Results:", results)

  return
#####################################################################




@task
def push_pyEnv(cluster):

  host = cluster.getHosts()[0]
  print(f"push_pyEnv host is {host}")

  # Push and install anything in dist folder
  dists = glob.glob(f'dist/*.tar.gz')
  for dist in dists:
     print("pushing python dist: ", dist)
     subprocess.run(["scp",dist,f"{host}:~"], stderr=subprocess.STDOUT) 
     lib = dist.split('/')[1]
     print(f"push_pyEnv installing module: {lib}")
     subprocess.run(["ssh",host,"pip3","install","--user",lib], stderr=subprocess.STDOUT) 
  return
#####################################################################




@task(max_retries=1, retry_delay=timedelta(seconds=10))
def start_dask(cluster) -> Client:

  # Only single host supported currently
  host = cluster.getHostsCSV()

  # Should this be specified in the Job? Possibly?
  #nprocs = cluster.nodeCount * cluster.PPN
  nprocs = cluster.PPN

  # Start a dask scheduler on the host
  port = "8786"

  # Use dask-ssh 
  opts = f"dask-ssh --nprocs {nprocs} {host} &"

  try:
    subprocess.Popen(["dask-ssh","--nprocs",str(nprocs),host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  except Exception as e:
    print("In start_dask during subprocess.run :" + str(e))
    traceback.print_stack()

  daskclient = Client(f"{host}:{port}")
  return daskclient
#####################################################################


def main() :
  return
#####################################################################


if __name__ == '__main__':
  main()
#####################################################################
