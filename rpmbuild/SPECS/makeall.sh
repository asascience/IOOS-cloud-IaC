#!/bin/sh

alist='
zlib.spec
libpng.spec
jasper.spec
hdf5.spec
'

nceplibs='
bacio.spec
bufr.spec
g2.spec
nemsio.spec
sigio.spec
w3emc.spec
w3nco.spec
'

utils='
netcdf.spec
wgrib2.spec
produtil.spec
'

compilers='
gcc.spec
'

models='
cbofs.spec
cbofs-devel.spec
'


# NCEPLIBS built folder
export BBASE=/home/ec2-user/nosofs-prereqs/BUILT

rpmlist="$alist $nceplibs $utils $compilers"

#rpmlist=$nceplibs
#rpmlist=$utils
#rpmlist='g2.spec'
rpmlist='cbofs-devel.spec'

for rpm in $rpmlist
do
    echo "==========================================="
    echo " Building rpm for $rpm"
    echo "==========================================="
  QA_RPATHS=$[ 0x0001|0x0010|0x0002 ] rpmbuild -bb $rpm
  if [[ $? -ne 0 ]] ; then
    echo "==========================================="
    echo " Error .... could not build $rpm"
    echo "==========================================="
    exit 1
  fi
  #mv /home/ec2-user/nosofs-prereqs/rpmbuild/RPMS/x86_64/*.rpm /home/ec2-user/nosofs-prereqs/RPMS
  #mv /home/$USER/nosofs-prereqs/rpmbuild/RPMS/x86_64/*.rpm /home/$USER/nosofs-prereqs/RPMS
  mv /home/$USER/rpmbuild/RPMS/x86_64/*.rpm ../../RPMS
  
done

