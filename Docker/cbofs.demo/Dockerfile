FROM centos:7
LABEL maintainer="patrick.tripp@rpsgroup.com"

# Setup base environment
RUN mkdir -p /ptmp ; chgrp wheel /ptmp ; chmod 775 /ptmp ;\
    mkdir -p /noscrub ; chgrp wheel /noscrub ; chmod 775 /noscrub ;\
    mkdir -p /save ; chgrp wheel /save ; chmod 775 /save ;\
    sed -i 's/tsflags=nodocs/# &/' /etc/yum.conf ;\
    yum -y install man-db man-pages \
        environment-modules \
        wget \
        tcsh \
        ksh ;\
    yum clean all ;\
    mkdir -p /usrx/modulefiles ;\
    . /usr/share/Modules/init/sh ;\
    echo /usrx/modulefiles | tee -a ${MODULESHOME}/init/.modulespath ;\
    echo . /usr/share/Modules/init/bash >> ~/.bashrc ;\
    echo source /usr/share/Modules/init/tcsh >> ~/.tcshrc ;\
    yum clean all

# Could save image here and reuse for next stages

#Intel package version has mixed internal versions
ARG ipkgver=2018.5.288
ARG impiver=2018.6.288

RUN mkdir -p /tmp/rpms; cd /tmp/rpms ;\
    curl https://ioos-cloud-sandbox.s3.amazonaws.com/public/libs/nosofs_base_rpms.gcc.6.5.0.el7.20191011.tgz | tar -xvz ;\
    yum -y install \
        gcc-6.5.0-1.el7.x86_64.rpm        \
        hdf5-1.8.21-1.el7.x86_64.rpm      \
        netcdf-4.2-1.el7.x86_64.rpm       \
        produtil-1.0.18-1.el7.x86_64.rpm ;\
    yum clean all ;\
    cd ~ ;\
    rm -Rf /tmp/rpms ;\

    mkdir -p /tmp/impi; cd /tmp/impi ;\
    curl https://ioos-cloud-sandbox.s3.amazonaws.com/public/libs/intel_mpi_2018.5.288.tgz | tar -xvz ;\    
    ./install.sh -s silent.cfg ;\
    cd ~ ;\
    rm -Rf /tmp/impi ;\
    mkdir -p /usrx/modulefiles/mpi/intel ;\
    cp -p /opt/intel/compilers_and_libraries_${impiver}/linux/mpi/intel64/modulefiles/mpi /usrx/modulefiles/mpi/intel/${impiver} ;\
    ;\
    chgrp -R wheel /save ; chmod -R g+w /save ;\
    mkdir -p /tmp/cbofs; cd /tmp/cbofs ;\
    wget https://ioos-cloud-sandbox.s3.amazonaws.com/public/cbofs/nosofs-cbofs-v3.1.9.1-1.el7.x86_64.rpm ;\
    yum -y install nosofs-cbofs-v3.1.9.1-1.el7.x86_64.rpm ;\
    cd ~; rm -Rf /tmp/cbofs ;\
    ;\
    mkdir -p /noscrub/com/nos ; cd /noscrub/com/nos ;\
    curl https://ioos-cloud-sandbox.s3.amazonaws.com/public/cbofs/ICs.cbofs.2019100100.tgz | tar -xvz ;\
    chgrp -R wheel /noscrub ;\
    chmod -R g+w /noscrub   


ARG username=cbofs

# Put this in entrypoint script
# User stuff
RUN useradd -m -g wheel -s /bin/bash ${username} ;\
    mkdir -p /ptmp ; chgrp wheel /ptmp ; chmod 775 /ptmp

USER $username
WORKDIR /home/${username}
RUN echo alias lsl ls -al >> ~/.tcshrc ;\ 
    echo alias lst ls -altr >> ~/.tcshrc ;\
    echo alias h history >> ~/.tcshrc ;\
    echo alias cds cd /save >> ~/.tcshrc ;\
    echo alias cdns cd /noscrub >> ~/.tcshrc ;\
    echo alias cdpt cd /ptmp >> ~/.tcshrc

# ENV USER=${username}

# Exploit https://nvd.nist.gov/vuln/detail/CVE-2019-5736
#metadata:
#  name: run-as-uid-1000
#spec:
#  securityContext:
#    runAsUser: 1000
