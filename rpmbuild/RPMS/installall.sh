#!/bin/sh

rlist='
gcc-6.5.0-1.el7.x86_64.rpm
bacio-v2.1.0-1.el7.x86_64.rpm
bufr-v11.0.2-1.el7.x86_64.rpm
g2-v3.1.0-1.el7.x86_64.rpm
hdf5-1.8.21-1.el7.x86_64.rpm
jasper-1.900.1-1.el7.x86_64.rpm
libpng-1.5.30-1.el7.x86_64.rpm
nemsio-v2.2.4-1.el7.x86_64.rpm
netcdf-4.2-1.el7.x86_64.rpm
produtil-1.0.18-1.el7.x86_64.rpm
sigio-v2.1.0-1.el7.x86_64.rpm
w3emc-v2.2.0-1.el7.x86_64.rpm
w3nco-v2.0.6-1.el7.x86_64.rpm
wgrib2-2.0.8-1.el7.x86_64.rpm
zlib-1.2.11-1.el7.x86_64.rpm
'

for rpm in $rlist
do

    echo; echo "-----------------------------------------";
    echo "Installing $rpm ..."
    echo "-----------------------------------------"; echo;
    if [[ $rpm == "libpng-1.5.30-1.el7.x86_64.rpm" ]] ; then
      rpm --force --install $rpm
    else
      rpm --install $rpm
    fi

done

