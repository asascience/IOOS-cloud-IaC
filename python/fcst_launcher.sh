#!/bin/bash
set -xa
ulimit -c unlimited
ulimit -s unlimited


if [ $# -ne 6 ] ; then
  echo "Usage: $0 YYYYMMDD HH NPROCS PPN HOSTS <cbofs|ngofs|liveocean>"
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
export NPROCS=$3
export PPN=$4
export HOSTS=$5
export OFS=$6


# Can put domain specific options here
case $OFS in
  liveocean)
    export HOMEnos=/save/LiveOcean
    export JOBDIR=$HOMEnos/jobs
    export JOBSCRIPT=$JOBDIR/fcstrun.sh
    export JOBARGS="$CDATE"
    break;;
  *)
    export HOMEnos=/save/nosofs-NCO
    export JOBDIR=$HOMEnos/jobs
    export JOBSCRIPT=$JOBDIR/fcstrun.sh
    export cyc=$HH
    export JOBARGS="$CDATE $HH"
    break;;
esac
 
export MPIOPTS="-nolocal -launcher ssh -hosts $HOSTS -np $NPROCS -ppn $PPN"
cd $JOBDIR

#$JOBDIR/fcstrun.sh $CDATE $HH
$JOBSCRIPT $JOBARGS
