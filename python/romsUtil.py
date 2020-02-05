import sys
import shutil
import re
import math
import datetime
import os
import subprocess
import json


debug = False

def readConfig(configfile) :
  ''' converts a JSON document to a python dictionary '''

  if debug: print(f"DEBUG: in romsUtil : configfile is: {configfile}")

  with open(configfile, 'r') as cf:
    cfDict = json.load(cf)

  if (debug) :
    print(json.dumps(cfDict, indent=4))
    print(str(cfDict))

  return cfDict
#####################################################################



def sedoceanin ( template, outfile, settings ) :
 
  with open(template, 'r') as infile :
    lines = infile.readlines()

  with open(outfile, 'w') as outfile :
    for line in lines:
      newline = line

      for key, value in settings.items() :
        #print('In sedoceanin :',key, ' ', value)
        newline = re.sub(key, str(value), newline) 

      outfile.write(re.sub(key, value, newline))

  return
#####################################################################




def makeOceanin(NPROCS,settings,template,outfile) :

  tiles = getTiling( NPROCS )

  reptiles = {
    "__NTILEI__"   : str(tiles["NtileI"]),
    "__NTILEJ__"   : str(tiles["NtileJ"]),
  }

  settings.update(reptiles)
  sedoceanin(template,outfile,settings)
  return
#######################################################################





def ndays( cdate1, cdate2 ) :

  dt = datetime.timedelta(days=0)
 
  y1 = int(cdate1[0:4])
  m1 = int(cdate1[4:6].lstrip("0"))
  d1 = int(cdate1[6:8].lstrip("0"))

  y2 = int(cdate2[0:4])
  m2 = int(cdate2[4:6].lstrip("0"))
  d2 = int(cdate2[6:8].lstrip("0"))

  # extended to include optional hours

  if len(cdate1) == 10:
    hh = cdate1[8:10]
    if hh == '00':
      h1 = 0
    else:
      h1 = int(cdate1[8:10].lstrip("0"))
  else:
    h1 = 0

  if len(cdate2) == 10:
    hh = cdate2[8:10]
    if hh == '00':
      h2 = 0
    else:
      h2 = int(cdate2[8:10].lstrip("0"))
  else:
    h2 = 0

  date1 = datetime.datetime(y1,m1,d1,h1)
  date2 = datetime.datetime(y2,m2,d2,h2)
  dt = date1 - date2

  days = dt.days   

  hour = dt.seconds/3600
  daysdec = hour / 24
  days = days + daysdec

  return str(days)
#####################################################################
  

def ndate_hrs( cdate, hours ):
  ''' return the YYYYMMDD for CDATE +/- hours '''

  y1 = int(cdate[0:4])
  m1 = int(cdate[4:6].lstrip("0"))
  d1 = int(cdate[6:8].lstrip("0"))

  hh = cdate[8:10]
  if hh == '00':
    h1 = 0
  else:
    h1 = int(cdate[8:10].lstrip("0"))

  dt = datetime.timedelta(hours=hours)

  date2 = datetime.datetime(y1,m1,d1,h1) + dt
  strdate = date2.strftime("%Y%m%d%H")

  return strdate
#####################################################################


def ndate( cdate, days ):
  ''' return the YYYYMMDD for CDATE +/- days '''

  y1 = int(cdate[0:4])
  m1 = int(cdate[4:6].lstrip("0"))
  d1 = int(cdate[6:8].lstrip("0"))

  dt = datetime.timedelta(days=days)
   
  date2 = datetime.date(y1,m1, d1) + dt
  strdate = date2.strftime("%Y%m%d")
  return strdate
#####################################################################





def lo_date( cdate ):
  ''' return the LiveOcean format of date e.g. f2019.11.06'''

  fdate = f"f{cdate[0:4]}.{cdate[4:6]}.{cdate[6:8]}"

  return fdate
#####################################################################
  



def getTiling( totalCores ) :
  ''' Algorithm

    prefer a square or closest to it

    It might be more optimal to have a ratio similar to the grid ratio

    if sqrt of total is an integer then use it for I and J
    if not find factorization closest to square

    examples:

      assert must be even, there are no even primes > 2
      36 = sqrt(36) = ceil(6)  36 mod 6 = 0 - DONE

      32 = sqrt(32) = 5.65 32 mod 6 != 0
                              mod 5 != 0
                              mod 4 == 0
                            32 / 4 = 8 DONE NtileI=8, NtileJ=4
  '''

  NtileI=1
  NtileJ=1

  #totalCores = coresPN * nodeCount
  print('In getTiling: totalCores = ', str(totalCores))

  if ((totalCores != 1) and (totalCores % 2 != 0)):
    raise Exception("Total cores must be even")

  square = math.sqrt(totalCores) 
  ceil = math.ceil(square)

  done="false"

  print("totalCores : ", totalCores)

  while (done == "false" ) :
    if ((totalCores % ceil) == 0) :
      NtileJ = ceil
      NtileI = int(totalCores / NtileJ)
      done="true"
    else:
      ceil -= 1

  print("NtileI : ", NtileI, " NtileJ ", NtileJ)

  return { "NtileI": NtileI, "NtileJ": NtileJ }
#####################################################################


def get_ICs_roms (ofs, cdate, cycle, localpath):

  # There is a shell script that already exists to do this
  # Can maybe re write it in Python later

  return



def get_ICs_lo( cdate, localpath, sshuser):
  ''' Get the atmospheric forcing and boundary layer conditions and ICs
      for LiveOcean ROMS model.

      This requires an account on the remote server with private key authentication.
  '''


  # TODO: Parameterize this
  restart_file = "ocean_his_0025.nc"
  remotepath = "/data1/parker/LiveOcean_output/cas6_v3"
  remotepath_rst = "/data1/parker/LiveOcean_roms/output/cas6_v3_lo8b"

  fdate = lo_date(cdate)
  prevdate = ndate(cdate, -1)
  fprevdate = lo_date(prevdate) 

  forceroot = f"{localpath}/forcing"
  forcedir = f"{forceroot}/{fdate}"

  if not os.path.exists(forcedir):
    os.makedirs(forcedir)
  else:
    print(f"Forcing directory {forcedir} already exists .... not downloading.")
    print(f"Remove the {forcedir} directory to force the download.")
    return
    

  # Get the forcing
  scpdir = f"{sshuser}:{remotepath}/{fdate}"


  # TODO: add exception handing, check return value from scp
  subprocess.run(["scp", "-rp", scpdir, forceroot], stderr=subprocess.STDOUT)

  # Instead of hardcoding path, create a symlink
  #SSFNAME == /com/liveocean/forcing/f2019.11.06/riv2/rivers.nc
  #SSFNAME == rivers.nc
  # ln -s {forcedir}/{fdate}/riv2/rivers.nc {localpath}/{fdate}/rivers.nc
  subprocess.run(["ln", "-s", f"{forcedir}/riv2/rivers.nc", \
                   f"{localpath}/{fdate}/rivers.nc"], stderr=subprocess.STDOUT)

  # Get the restart file from the previous day's forecast
  scpdir = f"{sshuser}:{remotepath_rst}/{fprevdate}"
  localdir = f"{localpath}/{fprevdate}"

  if not os.path.exists(localdir):
    os.mkdir(localdir)

  subprocess.run(["scp", "-p", f"{scpdir}/{restart_file}", localdir], stderr=subprocess.STDOUT)  

  return
#####################################################################

if __name__ == '__main__':
  pass 
