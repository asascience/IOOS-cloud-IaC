#!/bin/sh

rlist='
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
