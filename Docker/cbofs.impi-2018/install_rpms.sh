#!/bin/sh

#install the base rpms for model 
mkdir -p /tmp/rpms
cd /tmp/rpms
curl https://ioos-cloud-sandbox.s3.amazonaws.com/public/libs/nosofs_base_rpms.gcc.6.5.0.el7.20191011.tgz | tar -xvz
yum -y install \
    gcc-6.5.0-1.el7.x86_64.rpm \
    hdf5-1.8.21-1.el7.x86_64.rpm \
    netcdf-4.2-1.el7.x86_64.rpm \
    produtil-1.0.18-1.el7.x86_64.rpm
yum clean all
cd ~
rm -Rf /tmp/rpms
