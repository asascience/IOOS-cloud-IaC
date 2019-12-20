#!/bin/sh

# Retrieve 48 hour forecast from NOAA

if [ $# -lt 3 ] ; then
  echo "Usage: $0 cbOFS|ngOFS|etc. yyyymmdd hh [destination path]"
  exit 1
fi


OFS=$1
CDATE=$2
CYC=$3
if [ $# -gt 3 ]; then
  dest=$4
  mkdir -p $dest
  cd $dest
fi

#nos.$OFS.fields.f001.$CDATE.t${CYC}z.nc 
NOMADS=https://nomads.ncep.noaa.gov/pub/data/nccf/com/nos/prod/$OFS.$CDATE

#hlist='01 02 03 04 05 06 07 08 09'
hlist='01 06 12 18 24 36 48'

for hh in $hlist
do
  wget -nc $NOMADS/nos.$OFS.fields.f0$hh.$CDATE.t${CYC}z.nc
done

if [[ $OFS == "ngofs" ]] ; then
  wget -nc $NOMADS/nos.${OFS}.nestnode.*.forecast.$CDATE.t${CYC}z.nc
fi



#hh=10
#while [ $hh -le 48 ] ; do
#  wget -nc $NOMADS/nos.$OFS.fields.f0$hh.$CDATE.t${CYC}z.nc
#  hh=$(($hh+1))
#done

wget -nc $NOMADS/nos.$OFS.forecast.$CDATE.t${CYC}z.in
wget -nc $NOMADS/nos.$OFS.forecast.$CDATE.t${CYC}z.log

