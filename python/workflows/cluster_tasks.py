"""
"""

# Python dependencies
import glob
import logging
import sys
import os
import traceback
from os import subprocess

import time

from distributed import Client
from prefect.engine import signals
from prefect.triggers import all_finished

from LocalCluster import LocalCluster

log = logging.getLogger('workflow')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(' %(asctime)s  %(levelname)s - %(module)s.%(funcName)s | %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

from prefect.core import task

from AWSCluster import AWSCluster
from Cluster import Cluster

if os.path.abspath('..') not in sys.path:
    sys.path.append(os.path.abspath('..'))
curdir = os.path.dirname(os.path.abspath(__file__))


# cluster
@task
def cluster_init(config, provider) -> Cluster:
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


# cluster
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


# cluster
@task(trigger=all_finished)
def cluster_terminate(cluster):
    responses = cluster.terminate()
    # Just check the state
    log.info('Responses from terminate: ')
    for response in responses:
        pp.pprint(response)

    return


#######################################################################


# cluster
@task
def push_pyEnv(cluster):
    host = cluster.getHosts()[0]
    log.info(f"push_pyEnv host is {host}")

    # Push and install anything in dist folder
    dists = glob.glob(f'{curdir}/../dist/*.tar.gz')
    for dist in dists:
        log.info(f"pushing python dist: {dist}")
        subprocess.run(["scp", dist, f"{host}:~"], stderr=subprocess.STDOUT)

        path, lib = os.path.split(dist)
        log.info(f"push_pyEnv installing module: {lib}")

        subprocess.run(["ssh", host, "pip3", "install", "--upgrade", "--user", lib], stderr=subprocess.STDOUT)
    return


#####################################################################


# cluster
# @task(max_retries=0, retry_delay=timedelta(seconds=10))
@task
def start_dask(cluster) -> Client:
    # Only single host supported currently
    host = cluster.getHostsCSV()

    # Should this be specified in the Job? Possibly?
    # nprocs = cluster.nodeCount * cluster.PPN
    nprocs = cluster.PPN

    # Start a dask scheduler on the host
    port = "8786"

    log.info(f"host is {host}")

    if host == '127.0.0.1':
        log.info(f"in host == {host}")
        proc = subprocess.Popen(["dask-scheduler", "--host", host, "--port", port], \
                                # stderr=subprocess.DEVNULL)
                                stderr=subprocess.STDOUT)
        time.sleep(3)
        cluster.setDaskScheduler(proc)

        wrkrproc = subprocess.Popen(["dask-worker", "--nprocs", str(nprocs), "--nthreads", "1", \
                                     f"{host}:{port}"], stderr=subprocess.STDOUT)
        time.sleep(3)
        cluster.setDaskWorker(wrkrproc)

        daskclient = Client(f"{host}:{port}")
    else:
        # Use dask-ssh instead of multiple ssh calls
        # TODO: Refactor this, make Dask an optional part of the cluster
        # TODO: scale this to multiple hosts
        try:
            proc = subprocess.Popen(["dask-ssh", "--nprocs", str(nprocs), "--scheduler-port", port, host], \
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


# dask
@task
def dask_client_close(daskclient: Client):
    daskclient.close()
    return
