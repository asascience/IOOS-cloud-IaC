#!/bin/sh

# Retrieve 48 hour forecast from NOAA

#nos.cbofs.fields.f001.20191021.t00z.nc 
NOMADS=https://nomads.ncep.noaa.gov/pub/data/nccf/com/nos/prod/cbofs.20191021

hlist='01 02 03 04 05 06 07 08 09'

for hh in $hlist
do
  wget -nc $NOMADS/nos.cbofs.fields.f0$hh.20191021.t00z.nc
done


hh=10
while [ $hh -le 48 ] ; do
  wget -nc $NOMADS/nos.cbofs.fields.f0$hh.20191021.t00z.nc
  hh=$(($hh+1))
done

wget -nc $NOMADS/nos.cbofs.forecast.20191021.t00z.in
wget -nc $NOMADS/nos.cbofs.forecast.20191021.t00z.log

