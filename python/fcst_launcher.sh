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

export MPIOPTS="-launcher ssh -hosts $HOSTS -np $NPROCS -ppn $PPN"

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
    cd $JOBDIR
    export JOBARGS="ocean.in > ocean.out"
    mpirun $MPIOPTS $EXEC $JOBARGS
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
 
