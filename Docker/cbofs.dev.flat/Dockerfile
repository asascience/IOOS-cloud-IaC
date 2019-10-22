FROM centos:7
LABEL maintainer="patrick.tripp@rpsgroup.com"

# This is needed for Intel MPI 2019
ENV I_MPI_FABRICS=ofi
ARG impiver=2019.5.281
ARG ipkgver=2019.5.281

# Setup the base environment
RUN mkdir -p /ptmp ;\
chgrp wheel /ptmp ;\
chmod 775 /ptmp  ;\
mkdir -p /noscrub ;\
chgrp wheel /noscrub ;\
chmod 775 /noscrub ;\
mkdir -p /save ;\
chgrp wheel /save ;\
chmod 775 /save ;\
sed -i 's/tsflags=nodocs/# &/' /etc/yum.conf ;\
yum -y install man-db man-pages \
    environment-modules \
    glibc-devel \
    wget \
    tcsh \
    make ;\
#yum -y groupinstall "Development Tools" ;\
#yum -y erase gcc ;\
#yum -y erase gcc-c++ ;\
#yum -y erase gcc-gfortran ;\
#yum clean all ;\
mkdir -p /usrx/modulefiles ;\
. /usr/share/Modules/init/sh ;\
echo /usrx/modulefiles | tee -a ${MODULESHOME}/init/.modulespath ;\
echo . /usr/share/Modules/init/bash >>~/.bashrc ;\
echo source /usr/share/Modules/init/tcsh >>~/.tcshrc ;\
yum clean all ;\
# Install the libraries
mkdir -p /tmp/rpms ;\
cd /tmp/rpms ;\
curl https://ioos-cloud-sandbox.s3.amazonaws.com/public/libs/nosofs_base_rpms.gcc.6.5.0.el7.20191011.tgz | tar -xvz ;\
yum -y install \
    gcc-6.5.0-1.el7.x86_64.rpm \
    hdf5-1.8.21-1.el7.x86_64.rpm \
    netcdf-4.2-1.el7.x86_64.rpm \
    produtil-1.0.18-1.el7.x86_64.rpm ;\
yum clean all ;\
cd ~ ;\
rm -Rf /tmp/rpms ;\
# Install Intel MPI libraries
mkdir -p /tmp/intel_mpi ;\
cd /tmp/intel_mpi ;\
curl https://ioos-cloud-sandbox.s3.amazonaws.com/public/libs/intel_mpi_${impiver}.tgz | tar -xvz ;\
echo 'Starting Intel MPI silent install...'  ;\
./install.sh -s silent.cfg  ;\
echo '... Finished impi silent install'  ;\
mkdir -p /usrx/modulefiles/mpi/intel ;\
cp -p /opt/intel/compilers_and_libraries_${ipkgver}/linux/mpi/intel64/modulefiles/mpi /usrx/modulefiles/mpi/intel/${impiver} ;\
cd ~ ;\
rm -Rf /tmp/intel_mpi ;\
# Install the precompiled cbofs model, scripts, and demo ICs
mkdir -p /tmp/cbofs ;\
cd /tmp/cbofs ;\
wget https://ioos-cloud-sandbox.s3.amazonaws.com/public/cbofs/nosofs-cbofs-fcst-devel-v3.1.9.1-2.el7.x86_64.rpm ;\
yum -y install nosofs-cbofs-fcst-devel-v3.1.9.1-2.el7.x86_64.rpm ;\
cd ~ ;\
rm -Rf /tmp/cbofs ;\
mkdir -p /noscrub/com/nos ;\
cd /noscrub/com/nos ;\
curl https://ioos-cloud-sandbox.s3.amazonaws.com/public/cbofs/ICs.cbofs.2019100100.tgz | tar -xvz ;\
# Fix permissions so non-root user can modify
chgrp -R wheel /noscrub ;\
chmod -R g+w /noscrub ;\
chgrp -R wheel /save ;\
chmod -R g+w /save ;\
mkdir -p /ptmp ;\
chgrp wheel /ptmp ;\
chmod 775 /ptmp



ARG username=cbofs
RUN useradd -m -g wheel -s /bin/bash ${username}
USER $username

# Just set up some aliases
RUN echo alias lsl ls -al >> ~/.tcshrc ;\
echo alias lst ls -altr >> ~/.tcshrc ;\
echo alias h history >> ~/.tcshrc ;\
echo alias cds cd /save >> ~/.tcshrc ;\
echo alias cdns cd /noscrub >> ~/.tcshrc ;\
echo alias cdpt cd /ptmp >> ~/.tcshrc


