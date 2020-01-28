"""

Module of Prefect @task annotated functions for use in cloud based numerical 
weather modelling workflows. These tasks are basically wrappers around other
functions. Prefect forces some design choices.

Keep things cloud platform agnostic at this layer.
"""

# Python dependencies
import sys
import os
if os.path.abspath('..') not in sys.path:
    sys.path.append(os.path.abspath('..'))

import json
import pprint
import subprocess
import traceback
import glob
import time
import logging
from datetime import timedelta

from prefect import task, unmapped
from prefect.engine import signals
from prefect.triggers import all_successful, all_finished
from dask.distributed import Client

# Local dependencies
from cluster.Cluster import Cluster
from cluster.AWSCluster import AWSCluster
from cluster.LocalCluster import LocalCluster

from job.Job import Job
from job.ROMSForecast import ROMSForecast
from job.Plotting import Plotting

from services.CloudStorage import CloudStorage
from services.S3Storage import S3Storage

import romsUtil as util
from plotting import plot

pp = pprint.PrettyPrinter()
debug = False

log = logging.getLogger('workflow')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(' %(asctime)s  %(levelname)s - %(module)s.%(funcName)s | %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

  """
  Parameters
  ----------
  var : type
    Desc

  Returns
  -------
  var : type
    Desc

  Raises
  ------
  excep
    Desc

  Notes
  -----
  
  """

#######################################################################

@task
def storage_init(provider: str) -> CloudStorage :
  """Class factory that returns an implementation of CloudStorage.

  CloudStorage is the abstract base class that provides a generic interface for
  multiple cloud platforms. 
  
  Parameters
  ----------
  provider : str
    Name of an implemented provider.

  Returns
  -------
  service : CloudStorage
    Returns a specific implementation of the CloudStorage interface.

  Raises
  ------
  signals.FAIL
    Triggers and exception if `provider` is not supported.

  Notes
  -----
  The following providers are implemented:
    AWS S3 - S3Storage
  
  """

  if provider == 'AWS':
    service = S3Storage()
  
  elif provider == 'Local':
    log.error('Coming soon ...')
    raise signals.FAIL()
  else:
    log.error('Unsupported provider')
    raise signals.FAIL()

  return service
#######################################################################


# TODO: Parameterize filespecs?
@task
def save_to_cloud(job: Job, service: CloudStorage, filespecs: list, public=False):
  """ Save stuff to cloud storage.

  Parameters
  ----------
  job : Job
    A Job object that contains the required attributes:
      BUCKET - bucket name
      BCKTFOLDER - bucket folder
      CDATE - simulation date
      OUTDIR - source path 

  service : CloudStorage
    An implemented service for your cloud provider.

  filespec : list of strings
    file specifications to match using glob.glob
    Example: ["*.nc", "*.png"]

  public : bool, optional
    Whether the files should be made public. Default: False
  """
  
  BUCKET = job.BUCKET
  BCKTFLDR = job.BCKTFLDR
  CDATE = job.CDATE
  path = job.OUTDIR

  #Forecast output
  #ocean_his_0002.nc
  #folder = f"output/{job.CDATE}"
  #filespec = ['ocean_his_*.nc']

  for spec in filespecs:
    FILES = sorted(glob.glob(f"{path}/{spec}"))

    log.info('Uploading the following files:')
    
    for filename in FILES:
      print(filename)
      fhead, ftail = os.path.split(filename)
      key = f"{BCKTFLDR}/{CDATE}/{ftail}"
      
      service.upload_file(filename, BUCKET, key, public)
  return
#######################################################################



@task
def cluster_init(config, provider) -> Cluster :

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
def cluster_start(cluster):

  log.info('Starting ' + str(cluster.nodeCount) + ' instances ...')
  try:
    cluster.start()
  except Exception as e:
    log.exception('In driver: Exception while creating nodes :' + str(e))
    raise signals.FAIL()
  return
#######################################################################



@task(trigger=all_finished)
def cluster_terminate(cluster):

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



# TODO: make sshuser an optional Job parameter
# TODO: make this model agnostic
@task
def get_forcing(jobconfig: str, sshuser):
  """ jobconfig - filename of json file """

  # Open and parse jobconfig file
  #"OFS"       : "liveocean",
  #"CDATE"     : "20191106",
  #"ININAME"   : "/com/liveocean/f2019.11.05/ocean_his_0025.nc",

  jobDict = util.readConfig(jobconfig)
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
    log.error("Unsupported forecast: ", ofs)
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
  OUTDIR = job.OUTDIR
  EXEC = job.EXEC

  runscript="./fcst_launcher.sh"
 
  try:
    HOSTS=cluster.getHostsCSV()
  except Exception as e:
    log.exception('In driver: execption retrieving list of hostnames:' + str(e))
    raise signals.FAIL()

  try:
    result = subprocess.run([runscript,CDATE,HH,OUTDIR,str(NPROCS),str(PPN),HOSTS,OFS,EXEC], \
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

  log.info(f"In daskmake_plots {FILES}")

  log.info(f"Target is : {target}")
  if not os.path.exists(target):
    os.makedirs(target)

  idx = 0
  futures = []
  for filename in FILES:
    log.info(f"plotting filename: {filename}")
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
     log.info(f"pushing python dist: {dist}")
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
