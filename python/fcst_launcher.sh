#!/bin/bash
set -xa
ulimit -c unlimited
ulimit -s unlimited


if [ $# -ne 8 ] ; then
  echo "Usage: $0 YYYYMMDD HH COMOUT NPROCS PPN HOSTS <cbofs|ngofs|liveocean|adnoc>"
  exit 1
fi

#export I_MPI_DEBUG=${I_MPI_DEBUG:-0}
#export I_MPI_FABRICS=${I_MPI_FABRICS:-shm:ofi}
#export I_MPI_FABRICS=efa
#export FI_PROVIDER=efa
#export FI_PROVIDER=tcp

# This was created to launch a job via Python
# The Python scripts create the cluster on-demand 
# and submits this job with the list of hosts available.


export CDATE=$1
export HH=$2
export COMOUT=$3
export NPROCS=$4
export PPN=$5
export HOSTS=$6
export OFS=$7
export EXEC=$8

#OpenMPI
#mpirun --version
#mpirun (Open MPI) 2.1.0

#IntelMPI
#mpirun --version
#Intel(R) MPI Library for Linux* OS, Version 2017 Update 2 Build 20170125 (id: 16752)
#Copyright (C) 2003-2017, Intel Corporation. All rights reserved.

mpirun --version | grep Intel
impi=$?

mpirun --version | grep "Open MPI"
openmpi=$?


if [ $impi -eq 0 ]; then
  export MPIOPTS="-launcher ssh -hosts $HOSTS -np $NPROCS -ppn $PPN"
elif [ $openmpi -eq 0 ]; then
  #export MPIOPTS="-launch-agent ssh -host $HOSTS -n $NPROCS -npernode $PPN"
  export MPIOPTS="-host $HOSTS -np $NPROCS -npernode $PPN -oversubscribe"
else
  echo "ERROR: Unsupported mpirun version ..."
  exit 1
fi

#export MPIOPTS="-launcher ssh -hosts $HOSTS -np $NPROCS -ppn $PPN"
#export MPIOPTS="-hosts $HOSTS -np $NPROCS -ppn $PPN"

# Can put domain specific options here
case $OFS in
  liveocean)
    export HOMEnos=/save/LiveOcean
    export JOBDIR=$HOMEnos/jobs
    export JOBSCRIPT=$JOBDIR/fcstrun.sh
    export JOBARGS="$CDATE"
    cd $JOBDIR
    $JOBSCRIPT $JOBARGS
    ;;
  adnoc)
    export JOBDIR=$COMOUT
    mkdir -p $JOBDIR/output
    cd $JOBDIR
    mpirun $MPIOPTS $EXEC ocean.in > ocean.log
    ;;
  *)
    export HOMEnos=/save/nosofs-NCO
    export JOBDIR=$HOMEnos/jobs
    export JOBSCRIPT=$JOBDIR/fcstrun.sh
    export cyc=$HH
    export JOBARGS="$CDATE $HH"
    cd $JOBDIR
    $JOBSCRIPT $JOBARGS
    ;;
esac
 
