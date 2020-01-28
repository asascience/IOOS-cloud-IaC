#!/usr/bin/python3

import os
import glob

from prefect import Flow, task, unmapped
from prefect.engine.executors import DaskExecutor
from dask.distributed import Client

from plotting.plot import plot_roms


def main():
    
   
    SOURCE = os.path.abspath('/com/liveocean/current')
    TARGET = os.path.abspath('/com/liveocean/current/plots')

    #FILES = sorted([os.path.join(SOURCE, f) for f in os.listdir(SOURCE)])
    #FILES = FILES[:5]
    FILES = sorted(glob.glob(f'{SOURCE}/*.nc'))

    #FILES="/com/liveocean/current/ocean_his_0001.nc,
    # /com/liveocean/current/ocean_his_0002.nc"

    if not os.path.exists(TARGET):
        os.mkdir(TARGET)

    #with Flow('plotting') as flow:
    #    plot_roms.map(ncfile=FILES, target=unmapped(TARGET), varname=unmapped('temp'))
    for ncf in FILES:
      plot_roms(ncf,TARGET,'temp')


    # When calling dask-scheduler and dask-worker at the command line
    # address_tcp = 'tcp://10.90.69.73:8786'
    # print(address_tcp)
    # executor = DaskExecutor(address=address_tcp, local_processes=True, debug=True)

    # Defining the client in the script
    # client = Client()
    # print(client)
    # address_tcp = client.scheduler.address
    # executor = DaskExecutor(address=address_tcp)
    # flow.run(executor=executor)

    # Ignoring Dask
    #flow.run()

if __name__=='__main__':
    main()
