#!/bin/bash

module purge
module load gcc/6.5.0 
module load mpi/intel/2020.0.166
module load netcdf/4.5
module load hdf5/1.10.5 

curdir=$PWD
export ESMF_DIR=$curdir/esmf
export ESMF_INSTALL_PREFIX=/usrx/esmf/8.0.0

#export ESMF_BOPT=O  # g or O
#export ESMF_OPTLEVEL=4  # 0-4
export ESMF_COMM=intelmpi

# 8.3.2 NetCDF Options
export ESMF_NETCDF=split
export ESMF_NETCDF_INCLUDE=${NETCDF}/include
export ESMF_NETCDF_LIBPATH=${NETCDF}/lib
export ESMF_NETCDF_LIBS='-lnetcdf_c++4 -lnetcdf -lnetcdff'
                                                                 

# Test options
#ESMF_TESTEXHAUSTIVE:    OFF
export ESMF_TESTCOMPTUNNEL=ON
export ESMF_TESTWITHTHREADS=ON
export ESMF_TESTMPMD=ON
export ESMF_TESTSHAREDOBJ=ON
#ESMF_TESTFORCEOPENMP:   OFF
#ESMF_TESTFORCEOPENACC:  OFF

cd esmf
#gmake clean
#gmake info
#gmake -j4
#gmake check
#gmake install

#gmake build_apps
gmake install_apps

# Other gmake build targets
# lib build the ESMF libraries only (default)
# all build the libraries, unit and system tests and examples
# doc build the documentation (requires specific latex macros packages and additional utilities; see Section 8 for more details on the requirements).
# info print out extensive system configuration information about what compilers, libraries, paths, flags, etc are being used
# clean remove all files built for this platform/compiler/wordsize.
# clobber remove all files built for all architectures
# install install the ESMF library in a custom location

# Advice to installers. Complete the installation of ESMF by defining a single ESMF specific environment variable, named ESMFMKFILE. This variable shall point to the esmf.mk file that was generated during the installation process. Systems that support multiple ESMF installations via management software (e.g. modules, softenv, ...) shall set/reset variable ESMFMKFILE as part of the configuration.

# By default file esmf.mk is located next to the ESMF library file in directory ESMF_INSTALL_LIBDIR. Consequently, unless esmf.mk has been moved to a different location after the installation, the correct setting for ESMFMKFILE is $(ESMF_INSTALL_LIBDIR)/esmf.mk.
