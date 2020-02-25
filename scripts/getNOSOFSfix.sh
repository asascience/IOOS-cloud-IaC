#!/bin/bash

version="v3.2.1"
noaaurl="https://www.nco.ncep.noaa.gov/pmb/codes/nwprod/nosofs.${version}"

opts="-nc -np -r"

fixdirs="
fix/cbofs/
fix/dbofs/
fix/ngofs/
fix/negofs/
fix/nwgofs/
fix/shared/
"


fixdirs='
fix/leofs/
'

for dir in $fixdirs
do
  wget $opts $noaaurl/$dir
done


cd www.nco.ncep.noaa.gov
rm robots.txt
find . -name "index.html*" -exec rm -rf {} \;
cd ..

mv ./www.nco.ncep.noaa.gov/pmb/codes/nwprod/nosofs.${version} .
rm -Rf www.nco.ncep.noaa.gov

