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
from prefect import Flow, task, unmapped
from prefect.triggers import all_successful, all_finished
from prefect.engine.task_runner import TaskRunner
from dask.distributed import Client

# Local dependencies
from Cluster.AWSCluster import AWSCluster
import romsUtil as util

from plotting.plot import plot_roms

pp = pprint.PrettyPrinter()
debug = False


# Reuse
#######################################################################
@task
def init_cluster(config) -> AWSCluster :
  try:
    cluster = AWSCluster(config)
  except Exception as e:
    print('Could not create cluster: ' + str(e))
    sys.exit()
  return cluster
#######################################################################


# Reuse
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

# Reuse
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



# Reuse ? Only if parameterize hard coded paths/filenames
# NPROCS in JOB or NPROCS=totalCores in cluster? Who decides?
#######################################################################
# @ task : need to parameterize/objectify Job if to be made a task
# TODO: jobDesc file - paramter
def job_init(cluster) :

  # TODO: Move this into it's own routine, make it a function param
  jobDesc = "jobs/liveocean.job"

  PPN = cluster.getCoresPN()
  totalCores = cluster.nodeCount*PPN

  with open(jobDesc, 'r') as cf:
    jobDict = json.load(cf)

  if (debug) :
    print(json.dumps(jobDict, indent=4))
    print(str(jobDict))

  CDATE = jobDict['CDATE']
  HH = jobDict['HH']
  OFS = jobDict['OFS']
  TIME_REF = jobDict['TIME_REF']

  # TODO: Make ocean in for NOSOFS
  if OFS == 'liveocean':

    # TODO: NO HARDCODED PATHS!
    # LiveOcean requires a significant amount of available RAM to run > 16GB
    # NTIMES 90 is 1 hour for liveocean 
    # Using f-strings
    # Add stuff to the replacement dictionary 
    fdate = f"f{CDATE[0:4]}.{CDATE[4:6]}.{CDATE[6:8]}"
    template = f"templates/{OFS}.ocean.in"
    outfile = f"/com/liveocean/{fdate}/liveocean.in"

    DSTART = util.ndays(CDATE,TIME_REF)
    # DSTART = days from TIME_REF to start of forecast day larger minus smaller date

    settings = {
      "__NTIMES__"   : jobDict['NTIMES'],
      "__TIME_REF__" : jobDict['TIME_REF'],
      "__DSTART__"   : DSTART,
      "__FDATE__"    : fdate,
      "__ININAME__"  : "/com/liveocean/f2019.11.05/ocean_his_0025.nc"
    }

  elif cluster.OFS == 'cbofs':
    template = f"TODO-cbofstemplate"
    outfile = f"TODO-template"
  else :
    print("unsupported model")
    # TODO: Throw exception

  makeOceanin(totalCores,settings,template,outfile)

  return jobDict
#######################################################################



# Reuse if parameterized
# Customize
#######################################################################
# TODO - paramaterize this forecast run, add Job object
@task
def forecast_run(cluster):

  # Setup the job
  PPN = cluster.getCoresPN()
  NPROCS = cluster.nodeCount*PPN

  try:
    jobDict = job_init(cluster)
  except Exception as e:
    print('In forecast_run: execption from job_init: '+ str(e))
    traceback.print_stack()
    return False
    
  CDATE = jobDict['CDATE']
  HH = jobDict['HH']
  OFS = jobDict['OFS']

  runscript="fcst_launcher.sh"

  try:
    HOSTS=cluster.getHostsCSV()
  except Exception as e:
    print('In driver: execption retrieving list of hostnames:' + str(e))
    return False
    # TODO - check this error handling and refactor if needed

  try:
    subprocess.run([runscript,CDATE,HH,str(NPROCS),str(PPN),HOSTS,OFS], \
      stderr=subprocess.STDOUT)
  except Exception as e:
    print('In driver: Exception during subprocess.run :' + str(e))
    return False

  print('Forecast finished')
  return

#######################################################################



# Reuse
# TODO: Move this into romsUtils
#######################################################################
def makeOceanin(totalCores,settings,template,outfile) :

  # TODO - setup for NOSOFS

  tiles = util.getTiling( totalCores )

  reptiles = {
    "__NTILEI__"   : str(tiles["NtileI"]),
    "__NTILEJ__"   : str(tiles["NtileJ"]),
  }

  settings.update(reptiles)
  util.sedoceanin(template,outfile,settings)
  return
#######################################################################


# Reuse
#####################################################################

@task
def nc_files(SOURCE):
    FILES = sorted(glob.glob(f'{SOURCE}/*.nc'))
    for f in FILES:
      print(f)
    return FILES
#####################################################################




#####################################################################
@task
def make_plots(filename,target,varname):

  print(f"{filename} {target} {varname}")
  plot_roms(filename,target,varname)
  return
#####################################################################




#####################################################################
@task
def daskmake_plots(client: Client, FILES: list, target: str, varname:str ):

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



 # Customize
with Flow('ofs workflow') as flow:

  #####################################################################
  # FORECAST
  #####################################################################

  # TODO: make this a runtime argument?
  #config='./configs/liveocean.config'
  config='./configs/test.config'

  # Create the cluster object
  cluster = init_cluster(config)

  # Start the cluster
  fcStarted = start_cluster(cluster)

  # Run the forecast
  fcstStatus = forecast_run(cluster)

  # Terminate the cluster nodes
  fcTerminated = terminate_cluster(cluster)

  flow.add_edge(fcStarted,fcstStatus)
  flow.add_edge(fcstStatus,fcTerminated)


  #####################################################################
  # POST Processing
  #####################################################################
  # Spin up a new machine?
  # or launch a container?
  # or run concurrently on above?
  # or run on local machine?

  # TODO: Parameterize this! 
  SOURCE = os.path.abspath('/com/liveocean/current')
  TARGET = os.path.abspath('/com/liveocean/current/plots')
  FILES = nc_files(SOURCE, upstream_tasks=[fcstStatus])

  # Start a machine
  postconfig = './configs/post.config'
  postmach = init_cluster(postconfig)
  pmStarted = start_cluster(postmach, upstream_tasks=[fcstStatus])

  # Push the env, install required libs on post machine
  pushPy = push_pyEnv(postmach, upstream_tasks=[pmStarted])

  # Start a dask scheduler on the host
  daskclient = start_dask(postmach, upstream_tasks=[pushPy])

  # Make plots
  plots = daskmake_plots(daskclient, FILES, TARGET, 'temp')
  plots.set_upstream([daskclient])

  pmTerminated = terminate_cluster(postmach,upstream_tasks=[plots])


#####################################################################

def main():

  print(flow.tasks)
  flow.run()

#####################################################################

 
if __name__ == '__main__':
  main()
