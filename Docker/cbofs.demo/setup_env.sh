#!/bin/sh

# Setup base environment, shells, paths, and module support
mkdir -p /ptmp
chgrp wheel /ptmp
chmod 775 /ptmp
mkdir -p /noscrub
chgrp wheel /noscrub
chmod 775 /noscrub
mkdir -p /save
chgrp wheel /save
chmod 775 /save
sed -i 's/tsflags=nodocs/# &/' /etc/yum.conf
yum -y install man-db man-pages \
    environment-modules \
    wget \
    tcsh \
    ksh \
    sudo
yum clean all
mkdir -p /usrx/modulefiles
. /usr/share/Modules/init/sh
echo /usrx/modulefiles | tee -a ${MODULESHOME}/init/.modulespath
echo . /usr/share/Modules/init/bash >>~/.bashrc
echo source /usr/share/Modules/init/tcsh >>~/.tcshrc
yum clean all
