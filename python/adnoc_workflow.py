#!/usr/bin/env python3

# keep things cloud platform agnostic at this layer
import sys
import os
from Cluster.AWSCluster import AWSCluster
import pprint
import subprocess
import romsUtil as util

from prefect import Flow, task

pp = pprint.PrettyPrinter()


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



#######################################################################
@task
def start_cluster(cluster):

  print('Starting ' + str(cluster.nodeCount) + ' instances ...')
  try:
    cluster.start()
  except Exception as e:
    print('In driver: Exception while creating nodes :' + str(e))
    sys.exit()
  return cluster

#######################################################################




#######################################################################
# TODO - paramaterize this forecast run
@task
def forecast_run(cluster):

  # Shared libraries must be available to the executable!!! shell env is not preserved
  #runscript='/save/nosofs-NCO/jobs/launcher.sh'
  PPN = cluster.getCoresPN()
  NPROCS = cluster.nodeCount*PPN

  print('In forecast_run. PPN = ', str(PPN), ' NPROCS = ', str(NPROCS))

  # TODO: Read these from a job config file
  CDATE = cluster.CDATE
  HH = cluster.HH
  OFS = cluster.OFS
  RUNDIR = "/var/OFS/ROMS/adnoc.2019121200"
  EXEC = "/mnt/efs/ec2-user/roms-761/oceanM"
  oceanin = "ocean.in"

  # Make ocean in
  makeOceanin(cluster)


  try:
    HOSTS=cluster.getHostsCSV()
  except Exception as e:
    print('In driver: execption retrieving list of hostnames:' + str(e))
  # TODO - check this error handling and refactor if needed


  HOSTS='localhost'
  # This hack is needed since we don't have a clean Intel compiler and run-time installation
  LIBPATH = os.getenv('LD_LIBRARY_PATH')
  LIBPATH = LIBPATH + ':/opt/intel/psxe_runtime_2017.8.262/linux/compiler/lib/intel64_lin'
  os.putenv('LD_LIBRARY_PATH',LIBPATH)
  print('LD_LIBRARY_PATH : ', os.getenv('LD_LIBRARY_PATH'))

  # mpirun -n 1 /home/mmonim/roms-761/oceanM ocean.in > ocean.out 2>&1
  print('hostnames : ' + HOSTS)
  #MPIOPTS = " -nolocal -launcher ssh -hosts " + HOSTS + " -np " + str(NPROCS) + " -ppn " + str(PPN)
  MPIOPTS = "-launcher ssh -hosts " + HOSTS + " -np " + str(NPROCS) + " -ppn " + str(PPN) + " "

  # mpirun -env <ENVVAR> <value>
  print('mpirun', MPIOPTS, EXEC, oceanin);
  os.chdir(RUNDIR)

  #subprocess.run('echo $PWD',shell=True)
  #subprocess.run('which mpirun',shell=True)

  try:
    subprocess.run(['mpirun', '-launcher','ssh', '-hosts', HOSTS, '-np', str(NPROCS), \
                    '-ppn', str(PPN), EXEC, oceanin ], stderr=subprocess.STDOUT)
 
  except Exception as e:
    print('In driver: Exception during subprocess.run :' + str(e))

  print('Forecast finished')
  return 'DONE'

#######################################################################




#######################################################################
# TODO add a job config
#@task
def makeOceanin(cluster) :

  template="../adnoc/ocean.in.template"
  outfile="/var/OFS/ROMS/adnoc.2019121200/ocean.in"

  nodeCount = cluster.nodeCount
  coresPN = cluster.getCoresPN()
  totalCores = nodeCount * coresPN
  tiles = util.getTiling( totalCores )

  # Just a dictionary
  # Could also read this in from a json file 
  settings = {
    "__NTILEI__": tiles["NtileI"],
    "__NTILEJ__": tiles["NtileJ"],
    "__NTIMES__": 60,
    "__TIME_REF__": "20191212.00"
  }

  util.sedoceanin ( template, outfile, settings )

#######################################################################



#######################################################################
@task 
def terminate_cluster(cluster):

  
  responses = cluster.terminate()
  # Just check the state
  print('Responses from terminate: ')
  for response in responses :
    pp.pprint(response)
#######################################################################


#LIBPATH = os.getenv('LD_LIBRARY_PATH')
#LIBPATH = LIBPATH + ':/opt/intel/psxe_runtime_2017.8.262/linux/compiler/lib/intel64_lin'
#os.putenv('LD_LIBRARY_PATH',LIBPATH)


with Flow('ofs workflow') as flow:

  # Pre process tasks here


  # TODO: refactor the DAG instead of relying on the cluster object 
  # TODO: separate the cluster infrastructure config from the forecast job config
  config='./configs/adnoc.config'

  # Forecast
  cluster = init_cluster(config)

  #cluster = start_cluster(cluster)

  status = forecast_run(cluster)

  # Terminate the cluster nodes
  terminate_cluster(cluster)
  terminate_cluster(cluster).set_upstream(status)

  # Post process example
  #config = 'post.config'
  #postscript = 'poststub'

  #post_machine = init_cluster(config)
  #start_cluster(post_machine)
  #post_run(post_machine,postscript)

 
flow.run()



