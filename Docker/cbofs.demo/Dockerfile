FROM centos:7
LABEL maintainer="patrick.tripp@rpsgroup.com"

# Setup base environment and install dependencies
COPY setup_env.sh      /tmp/
COPY install_rpms.sh   /tmp/rpms/
COPY install_impi.sh   /tmp/intel_mpi/
COPY install_cbofs.sh  /tmp/cbofs/

# This is needed for Intel MPI 2019, shm does not work
# Issue is likely related to glibc and how shared memory is allocated
ENV I_MPI_FABRICS=ofi

# Install the model (CBOFS) and sample ICs last
RUN cd /tmp ;\
    ./setup_env.sh ;\
    cd /tmp/rpms ;\
    ./install_rpms.sh ;\
    cd /tmp/intel_mpi ;\
    ./install_impi.sh ;\
    cd /tmp/cbofs ;\
    ./install_cbofs.sh ;\

COPY user-aliases.sh /usr/local/bin/

ARG username=cbofs
RUN useradd -m -g wheel -s /bin/bash ${username}
USER $username

RUN /usr/local/bin/user-aliases.sh
