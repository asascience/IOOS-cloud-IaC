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
def job_init(cluster, configfile) -> dict :

  PPN = cluster.getCoresPN()
  totalCores = cluster.nodeCount*PPN

  with open(configfile, 'r') as cf:
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
    outfile = f"/com/{OFS}/{fdate}/liveocean.in"

    # Add this to dictionary
    jobDict['COMOUT'] = f"/com/{OFS}/{fdate}"

    DSTART = util.ndays(CDATE,TIME_REF)
    # DSTART = days from TIME_REF to start of forecast day larger minus smaller date

    # TODO : parameterize this ININAME
    settings = {
      "__NTIMES__"   : jobDict['NTIMES'],
      "__TIME_REF__" : jobDict['TIME_REF'],
      "__DSTART__"   : DSTART,
      "__FDATE__"    : fdate,
      "__ININAME__"  : jobDict['ININAME']
    }

  elif cluster.OFS == 'cbofs':
    template = f"TODO-cbofstemplate"
    outfile = f"TODO-template"
  else :
    print("unsupported model")
    # TODO: Throw exception

  # Make the .in file
  util.makeOceanin(totalCores,settings,template,outfile)

  return jobDict
#######################################################################




# TODO, make job class and use object here
@task
def forecast_run(cluster, jobDict):

  # Setup the job
  PPN = cluster.getCoresPN()
  NPROCS = cluster.nodeCount*PPN


  CDATE = jobDict['CDATE']
  HH = jobDict['HH']
  OFS = jobDict['OFS']

  runscript="fcst_launcher.sh"
  
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
    print('Forecast failed ...')
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
def make_plots(filename,target,varname):

  print(f"{filename} {target} {varname}")
  plot_roms(filename,target,varname)
  return
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
