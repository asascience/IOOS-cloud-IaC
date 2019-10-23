#!/bin/sh
set -e

curdir=$PWD

module load produtil

COMDIR=/noscrub/com/nos
NOSDIR=/save/nosofs.v3.1.9.1

curcycle=$(./getCurrentCycleOps.sh)
prevcycle=$(ndate -6 $curcycle)

echo Current: $curcycle
echo Previous: $prevcycle

echo "Fetching ICs for $prevcycle"
cdate=$(echo $prevcycle | cut -c1-8)
cyc=$(echo $prevcycle | cut -c9-10)

# Get the ICs
./getICs_cbofs.sh $cdate $cyc

# Change the roms.in file, tiles and run length
cd $COMDIR/cbofs.$cdate

romsin=nos.cbofs.forecast.${cdate}.t${cyc}z.in
romssave=nos.cbofs.forecast.${cdate}.t${cyc}z.in.save
cp -p $romsin $romssave


Itiles=8
Jtiles=12
#NTIMES=720   # 6 hour
NTIMES=120   # 1 hour

# Replace tiles and ntimes with custom setting
# Safest and most reusable way, just delete any matching lines

sed -i '/NtileI/d' $romsin
sed -i '/NtileJ/d' $romsin
echo "NtileI == $Itiles" >> $romsin
echo "NtileJ == $Jtiles" >> $romsin

sed -i '/NTIMES/d' $romsin
echo "NTIMES == $NTIMES" >> $romsin

# Launch the forecast
export NPP=$(($Itiles * $Jtiles))

cd $NOSDIR/jobs
./fcstrun.sh $cdate $cyc

# Copy results to S3 bucket using aws-cli
./copyResults2S3.sh $COMDIR $cdate $cyc

# Send a shutdown signal
# sudo shutdown

