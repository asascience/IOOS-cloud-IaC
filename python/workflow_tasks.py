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
import time
import logging

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

log = logging.getLogger('workflow')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(' %(asctime)s  %(levelname)s - %(module)s.%(funcName)s %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


@task
def init_cluster(config, provider) -> Cluster :

  if provider == 'AWS':

    try:
      cluster = AWSCluster(config)
    except Exception as e:
      log.exception('Could not create cluster: ' + str(e))
      raise signals.FAIL()

  elif provider == 'Local':
    cluster = LocalCluster(config)

  return cluster
#######################################################################



@task
def start_cluster(cluster):

  log.info('Starting ' + str(cluster.nodeCount) + ' instances ...')
  try:
    cluster.start()
  except Exception as e:
    log.exception('In driver: Exception while creating nodes :' + str(e))
    raise signals.FAIL()
  return
#######################################################################



@task(trigger=all_finished)
def terminate_cluster(cluster):

  responses = cluster.terminate()
  # Just check the state
  log.info('Responses from terminate: ')
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
    log.error("Unsupported job type")
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
      log.exception('Problem encountered with downloading forcing data ...')
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
    log.exception('In driver: execption retrieving list of hostnames:' + str(e))
    raise signals.FAIL()

  try:
    result = subprocess.run([runscript,CDATE,HH,str(NPROCS),str(PPN),HOSTS,OFS], \
      stderr=subprocess.STDOUT)

    if result.returncode != 0 :
      log.exception('Forecast failed ... result: ', result)
      raise signals.FAIL()

  except Exception as e:
    log.exception('In driver: Exception during subprocess.run :' + str(e))
    raise signals.FAIL()

  log.info('Forecast finished successfully')
  return 
#######################################################################



@task
def ncfiles_glob(SOURCE):
    FILES = sorted(glob.glob(f'{SOURCE}/*.nc'))
    for f in FILES:
      log.info('found the following files:')
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

  log.info(f"plotting {filename} {target} {varname}")
  plot.plot_roms(filename,target,varname)
  return
#####################################################################




@task
def daskmake_plots(client: Client, FILES: list, plotjob: Job ):

  target = plotjob.OUTDIR

  # TODO: implement multiple VARS in Job
  varname = plotjob.VARS[0]

  log.info("In daskmake_plots", FILES)

  log.info("Target is : ", target)
  if not os.path.exists(target):
    os.makedirs(target)

  idx = 0
  futures = []
  for filename in FILES:
    log.info("plotting filename: ", filename)
    future = client.submit(plot.plot_roms, filename, target, varname)
    futures.append(future)
    log.info(futures[idx])
    idx += 1
  
  for future in futures:
    result = future.result()
    log.info(result)

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
  log.info(f"push_pyEnv host is {host}")

  # Push and install anything in dist folder
  dists = glob.glob(f'dist/*.tar.gz')
  for dist in dists:
     log.info("pushing python dist: ", dist)
     subprocess.run(["scp",dist,f"{host}:~"], stderr=subprocess.STDOUT) 
     lib = dist.split('/')[1]
     log.info(f"push_pyEnv installing module: {lib}")
     subprocess.run(["ssh",host,"pip3","install","--user",lib], stderr=subprocess.STDOUT) 
  return
#####################################################################



@task
def dask_client_close( daskclient : Client ):
  daskclient.close()
  return


#@task(max_retries=0, retry_delay=timedelta(seconds=10))
@task
def start_dask(cluster) -> Client:

  # Only single host supported currently
  host = cluster.getHostsCSV()

  # Should this be specified in the Job? Possibly?
  #nprocs = cluster.nodeCount * cluster.PPN
  nprocs = cluster.PPN

  # Start a dask scheduler on the host
  port = "8786"

  log.info(f"host is {host}")

  if host == '127.0.0.1':
    log.info(f"in host == {host}")
    proc = subprocess.Popen(["dask-scheduler","--host", host, "--port", port], \
             #stderr=subprocess.DEVNULL)
             stderr=subprocess.STDOUT)
    time.sleep(3)
    cluster.setDaskScheduler(proc)

    wrkrproc = subprocess.Popen(["dask-worker","--nprocs",str(nprocs),"--nthreads", "1", f"{host}:{port}"], \
             stderr=subprocess.STDOUT)
      #stderr=subprocess.DEVNULL)
    time.sleep(3)
    cluster.setDaskWorker(wrkrproc)

    daskclient = Client(f"{host}:{port}")
  else:
    # Use dask-ssh instead of multiple ssh calls
    # TODO: Refactor this, make Dask an optional part of the cluster
    # TODO: scale this to multiple hosts
    try:
      proc = subprocess.Popen(["dask-ssh","--nprocs",str(nprocs),"--scheduler-port", port, host], \
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

      log.info('Connecting a dask client ')

      # Keep a reference to this process so we can kill it later
      cluster.setDaskScheduler(proc)
      daskclient = Client(f"{host}:{port}")
    except Exception as e:
      log.info("In start_dask during subprocess.run :" + str(e))
      traceback.print_stack()

  return daskclient
#####################################################################


def main() :
  return
#####################################################################


if __name__ == '__main__':
  main()
#####################################################################
