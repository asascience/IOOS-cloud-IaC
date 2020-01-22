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
from Cluster.LocalCluster import LocalCluster
from Cluster.Cluster import Cluster
from Job import Job
from Job.ROMSForecast import ROMSForecast
from Job.Plotting import Plotting

import romsUtil as util

from plotting import plot
#from plotting.plot import plot_roms

pp = pprint.PrettyPrinter()
debug = False


@task
def init_cluster(config, provider) -> Cluster :

  if provider == 'AWS':

    # TODO later: implement AzureCluster
    try:
      cluster = AWSCluster(config)
    except Exception as e:
      print('Could not create cluster: ' + str(e))
      raise signals.FAIL()

  elif provider == 'Local':
    cluster = LocalCluster(config)

  return cluster
#######################################################################



@task
def start_cluster(cluster):

  print('Starting ' + str(cluster.nodeCount) + ' instances ...')
  try:
    cluster.start()
  except Exception as e:
    print('In driver: Exception while creating nodes :' + str(e))
    raise signals.FAIL()
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
    raise signals.FAIL()

  return job
#######################################################################




@task
def get_forcing(jobconfig, sshuser):

  # Open and parse jobconfig file
  #"OFS"       : "liveocean",
  #"CDATE"     : "20191106",
  #"ININAME"   : "/com/liveocean/f2019.11.05/ocean_his_0025.nc",

  jobDict = Job.readConfig(jobconfig)
  cdate = jobDict['CDATE']
  ofs = jobDict['OFS']
  comrot = jobDict['COMROT']

  if ofs == 'liveocean':

    localpath = f"{comrot}/{ofs}"

    try: 
      util.get_forcing_lo(cdate, localpath, sshuser) 
    except Exception as e:
      print('Problem encountered with downloading forcing data ...')
      raise signals.FAIL() 

  else:
    raise signals.FAIL()

  # TODO: Add NOSOFS, can also use bash scripts that already exist
 
  return



@task
def forecast_run(cluster, job):

  PPN = cluster.getCoresPN()

  # Easier to read
  CDATE = job.CDATE
  HH = job.HH
  OFS = job.OFS
  NPROCS = job.NPROCS

  runscript="fcst_launcher.sh"
 
  try:
    HOSTS=cluster.getHostsCSV()
  except Exception as e:
    print('In driver: execption retrieving list of hostnames:' + str(e))
    raise signals.FAIL()

  try:
    result = subprocess.run([runscript,CDATE,HH,str(NPROCS),str(PPN),HOSTS,OFS], \
      stderr=subprocess.STDOUT)

    if result.returncode != 0 :
      print('Forecast failed ... result: ', result)
      raise signals.FAIL()

  except Exception as e:
    print('In driver: Exception during subprocess.run :' + str(e))
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
    SOURCE = job.INDIR
    FILES = sorted(glob.glob(f'{SOURCE}/*.nc'))
    return FILES
#####################################################################



@task
def make_plots(filename,target,varname):

  print(f"{filename} {target} {varname}")
  plot.plot_roms(filename,target,varname)
  return
#####################################################################




@task
def daskmake_plots(client: Client, FILES: list, plotjob: Job ):

  target = plotjob.OUTDIR

  # TODO: implement multiple VARS in Job
  varname = plotjob.VARS[0]

  print("In daskmake_plots", FILES)

  print("Target is : ", target)
  if not os.path.exists(target):
    os.makedirs(target)

  idx = 0
  futures = []
  for filename in FILES:
    print("plotting filename: ", filename)
    future = client.submit(plot.plot_roms, filename, target, varname)
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

  print(f"host is {host}")

  if host == 'localhost':
    print(f"in host == localhost")
    daskclient = Client()
  else:
    # Use dask-ssh instead of multiple ssh calls
    # TODO: Refactor this, make Dask an optional part of the cluster
    # TODO: scale this to multiple hosts
    try:
      proc = subprocess.Popen(["dask-ssh","--nprocs",str(nprocs),host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

      print('Connecting a dask client ')
      cluster.setDaskScheduler(proc)
      daskclient = Client(f"{host}:{port}")
    except Exception as e:
      print("In start_dask during subprocess.run :" + str(e))
      traceback.print_stack()

  return daskclient
#####################################################################


def main() :
  return
#####################################################################


if __name__ == '__main__':
  main()
#####################################################################
