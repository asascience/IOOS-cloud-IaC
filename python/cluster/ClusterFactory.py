import json
import logging

from prefect.engine import signals

from cluster import AWSCluster
from cluster import Cluster
from cluster import LocalCluster

debug = True

log = logging.getLogger('workflow')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(' %(asctime)s  %(levelname)s - %(module)s.%(funcName)s | %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

class ClusterFactory:

    def __init__(self):
        return

    def cluster(self, configfile) -> Cluster:

        cluster = None

        cfdict = self.readconfig(configfile)

        provider = cfdict['platform']

        if provider == 'AWS':
            try:
                cluster = AWSCluster(configfile)
            except Exception as e:
                log.exception('Could not create cluster: ' + str(e))
                raise signals.FAIL()
        elif provider == 'Local':
            cluster = LocalCluster(configfile)

        return cluster


    def readconfig(self,configfile):

        with open(configfile, 'r') as cf:
            cfdict = json.load(cf)

        if debug:
            print(json.dumps(cfdict, indent=4))
            print(str(cfdict))

        return cfdict
