#!/bin/sh

rlist='
hdf5-1.10.5-4.el7.x86_64.rpm
libpng-1.5.30-2.el7.x86_64.rpm
'

for rpm in $rlist
do

    echo; echo "-----------------------------------------";
    echo "Checking $rpm ..."
    echo "-----------------------------------------"; echo;
    rpmlint $rpm
    read -rsn1 -p"Press any key to continue..."; echo

done

echo "Check complete."
