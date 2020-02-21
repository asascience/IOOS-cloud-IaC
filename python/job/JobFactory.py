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

        cfdict = self.readconfig(configfile)
        jobtype = cfdict['jobtype']

        if jobtype == 'romsforecast':
            newjob = ROMSForecast(configfile, NPROCS)
        elif jobtype == 'plotting':
            newjob = Plotting(configfile, NPROCS)
        else:
            raise Exception('Unsupported jobtype')

        return newjob


    def readconfig(self,configfile):

        with open(configfile, 'r') as cf:
            cfdict = json.load(cf)

        if debug:
            print(json.dumps(cfdict, indent=4))
            print(str(cfdict))

        return cfdict
