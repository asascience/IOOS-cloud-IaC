#!/bin/sh

# Retrieve 48 hour forecast from NOAA

if [ $# -lt 3 ] ; then
  echo "Usage: $0 cbofs|ngofs|etc. yyyymmdd cycle [destination path]"
  exit 1
fi


ofs=$1
cdate=$2
cyc=$3
if [ $# -gt 3 ]; then
  dest=$4
  mkdir -p $dest
  cd $dest
fi

#nos.$ofs.fields.f001.$cdate.t${cyc}z.nc 
NOMADS=https://nomads.ncep.noaa.gov/pub/data/nccf/com/nos/prod/$ofs.$cdate

#hlist='01 02 03 04 05 06 07 08 09'
hlist='01 06 12 18 24 36 48'

for hh in $hlist
do
  wget -nc $NOMADS/nos.$ofs.fields.f0$hh.$cdate.t${cyc}z.nc
done


#hh=10
#while [ $hh -le 48 ] ; do
#  wget -nc $NOMADS/nos.$ofs.fields.f0$hh.$cdate.t${cyc}z.nc
#  hh=$(($hh+1))
#done

wget -nc $NOMADS/nos.$ofs.forecast.$cdate.t${cyc}z.in
wget -nc $NOMADS/nos.$ofs.forecast.$cdate.t${cyc}z.log

