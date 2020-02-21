import json

from job.Plotting import Plotting
from job.ROMSForecast import ROMSForecast

from Job import Job

debug = True

class JobFactory:

    def __init__(self):
        return


    def job(self, configfile: str, NPROCS: int) -> Job:

        newjob = None

        cfDict = readConfig(configfile)
        jobtype = cfDict['jobtype']

        if jobtype == 'romsforecast':
            newjob = ROMSForecast(configfile, NPROCS)
        elif jobtype == 'plotting':
            newjob = Plotting(configfile, NPROCS)
        else:
            raise Exception('Unsupported jobtype')

        return newjob



def readConfig(configfile):

    with open(configfile, 'r') as cf:
        cfDict = json.load(cf)

    if (debug):
        print(json.dumps(cfDict, indent=4))
        print(str(cfDict))

    return cfDict