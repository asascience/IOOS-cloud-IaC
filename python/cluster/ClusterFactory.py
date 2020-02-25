import json
import logging

from prefect.engine import signals

from cluster.Cluster import Cluster
from cluster.AWSCluster import AWSCluster
from cluster.LocalCluster import LocalCluster

debug = True

log = logging.getLogger('workflow')
log.setLevel(logging.DEBUG)

class ClusterFactory:

    def __init__(self):
        return


    def cluster(self,configfile):

        cfdict = self.readconfig(configfile)

        provider = cfdict['platform']

        if provider == 'AWS':

            try:
                print('Attempting to make a newcluster :', provider)
                newcluster = AWSCluster(configfile)
            except Exception as e:
                log.exception('Could not create cluster: ' + str(e))
                raise signals.FAIL()
        elif provider == 'Local':
            newcluster = LocalCluster(configfile)

        print("About to return from factory.cluster")
        return newcluster



    def readconfig(self,configfile):

        with open(configfile, 'r') as cf:
            cfdict = json.load(cf)

        if debug:
            print(json.dumps(cfdict, indent=4))
            print(str(cfdict))

        return cfdict