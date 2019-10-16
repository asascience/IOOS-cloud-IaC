#!/bin/sh

# Newer MPI is not working on Docker container for some reason
# 2019 Version - Not working with Docker - currently investigating
#impiver=2019.5.281
#ipkgver=2019.5.281

# Version 2018 has a typo/mismatch in path names - this version works with the newer build also

impiver=2018.5.288
ipkgver=2018.6.288

#COPY ./intel_mpi_2018.5.288/ /root/intel_mpi_2018.5.288
#RUN cd /root/intel_mpi_2018.5.288; ./install.sh -s silent.cfg ;\
#    mkdir -p /usrx/modulefiles/mpi/intel ;\
#    cp -p /opt/intel/compilers_and_libraries_2018.6.288/linux/mpi/intel64/modulefiles/mpi /usrx/modulefiles/mpi/intel/2018.6.288

mkdir -p /tmp/intel_mpi
cd /tmp/intel_mpi
curl https://ioos-cloud-sandbox.s3.amazonaws.com/public/libs/intel_mpi_${impiver}.tgz | tar -xvz

echo 'Starting Intel MPI silent install...'
./install.sh -s silent.cfg
echo '... Finished impi silent install'

# Copy the modulefile
mkdir -p /usrx/modulefiles/mpi/intel
cp -p /opt/intel/compilers_and_libraries_${ipkgver}/linux/mpi/intel64/modulefiles/mpi /usrx/modulefiles/mpi/intel/${impiver}

cd ~
rm -Rf /tmp/intel_mpi

