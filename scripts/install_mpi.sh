#!/bin/sh

ipkgver=2018.5.288
impiver=2018.6.288
#cd intel_mpi_$ipkgver
#sudo ./install.sh -s silent.cfg

sudo mkdir -p /usrx/modulefiles/mpi/intel
sudo cp -p /opt/intel/compilers_and_libraries_$impiver/linux/mpi/intel64/modulefiles/mpi /usrx/modulefiles/mpi/intel/$impiver
