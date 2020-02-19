"""
"""
# Python dependencies
import logging
import sys
import os

if os.path.abspath('..') not in sys.path:
    sys.path.append(os.path.abspath('..'))
curdir = os.path.dirname(os.path.abspath(__file__))

import glob

from prefect import task

from plotting import plot

from job.Job import Job
from job.ROMSForecast import ROMSForecast
from job.Plotting import Plotting

log = logging.getLogger('workflow')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(' %(asctime)s  %(levelname)s - %(module)s.%(funcName)s | %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


# generic, should be job
@task
def ncfiles_glob(SOURCE, filespec: str = "*.nc"):
    FILES = sorted(glob.glob(f'{SOURCE}/{filespec}'))
    for f in FILES:
        log.info('found the following files:')
        print(f)
    return FILES


#####################################################################


# job
@task
def ncfiles_from_Job(job: Job):
    SOURCE = job.INDIR
    filespec = job.FSPEC
    FILES = sorted(glob.glob(f'{SOURCE}/{filespec}'))
    return FILES


#####################################################################


# generic
@task
def make_plots(filename, target, varname):
    log.info(f"plotting {filename} {target} {varname}")
    plot.plot_roms(filename, target, varname)
    return


#####################################################################


# job
@task
def make_mpegs(job: Job):
    # TODO: make the filespec a function parameter
    for var in job.VARS:
        source = f"{job.OUTDIR}/ocean_his_%04d_{var}.png"
        target = f"{job.OUTDIR}/{var}.mp4"
        plot.png_ffmpeg(source, target)
    return


# job
# TODO: make sshuser an optional Job parameter
# TODO: make this model agnostic
@task
def get_forcing(job: Job, sshuser=None):
    """ job - Job object """

    # Open and parse jobconfig file
    # "OFS"       : "liveocean",
    # "CDATE"     : "20191106",
    # "ININAME"   : "/com/liveocean/f2019.11.05/ocean_his_0025.nc",

    # jobDict = util.readConfig(jobconfig)
    cdate = job.CDATE
    ofs = job.OFS
    comrot = job.COMROT
    hh = job.HH

    if ofs == 'liveocean':
        comdir = f"{comrot}/{ofs}"
        try:
            util.get_ICs_lo(cdate, comdir, sshuser)
        except Exception as e:
            log.exception('Problem encountered with downloading forcing data ...')
            raise signals.FAIL()

    elif ofs in ('cbofs', 'dbofs'):
        comdir = f"{comrot}/{ofs}.{cdate}"
        script = f"{curdir}/../../scripts/getICsROMS.sh"

        # echo "Usage: $0 YYYYMMDD HH cbofs|(other ROMS model) COMDIR"
        result = subprocess.run([script, cdate, hh, ofs, comdir], stderr=subprocess.STDOUT)
        if result.returncode != 0:
            log.exception(f'Retrieving ICs failed ... result: {result.returncode}')
            raise signals.FAIL()

    else:
        log.error("Unsupported forecast: ", ofs)
        raise signals.FAIL()

    return


#######################################################################


# job, dask
@task
def daskmake_mpegs(client: Client, job: Job):
    log.info(f"In daskmake_mpegs")

    # TODO: make the filespec a function parameter
    if not os.path.exists(job.OUTDIR):
        os.makedirs(job.OUTDIR)

    idx = 0
    futures = []

    for var in job.VARS:
        # source = f"{job.OUTDIR}/ocean_his_%04d_{var}.png"
        source = f"{job.OUTDIR}/f%03d_{var}.png"
        target = f"{job.OUTDIR}/{var}.mp4"

        log.info(f"Creating movie for {var}")
        log.info(f"source:{source} target:{target}")
        future = client.submit(plot.png_ffmpeg, source, target)
        futures.append(future)
        log.info(futures[idx])
        idx += 1

    # Wait for the jobs to complete
    for future in futures:
        result = future.result()
        log.info(result)

    return


#######################################################################


# job, dask
@task
def daskmake_plots(client: Client, FILES: list, job: Job):
    target = job.OUTDIR

    log.info(f"In daskmake_plots {FILES}")

    log.info(f"Target is : {target}")
    if not os.path.exists(target):
        os.makedirs(target)

    idx = 0
    futures = []

    # Submit all jobs to the dask scheduler
    # TODO - parameterize filespec and get files here?
    for filename in FILES:
        for varname in job.VARS:
            log.info(f"plotting file: {filename} var: {varname}")
            future = client.submit(plot.plot_roms, filename, target, varname)
            futures.append(future)
            log.info(futures[idx])
            idx += 1

    # Wait for the jobs to complete
    for future in futures:
        result = future.result()
        log.info(result)

    # Was unable to get it to work using client.map() gather
    # filenames = FILES[0:1]
    # print("mapping plot_roms over filenames")
    # futures = client.map(plot_roms, filenames, pure=False, target=unmapped(target), varname=unmapped(varname))
    # print("Futures:",futures)
    # Wait for the processes to finish, gather the results
    # results = client.gather(futures)
    # print("gathered results")
    # print("Results:", results)

    return
#####################################################################
