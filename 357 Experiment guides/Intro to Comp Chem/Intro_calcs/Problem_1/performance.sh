#!/bin/bash 

# The simple scipt creates a directory tree for METHODS/basis-set
# creates an input file and executes gaussian. After job completion
# it collects the energies and number of functions into performance.dat 
# file

# Written By MM
# NYC Feb 2019

printf "%10s%10s%10s%12s\n" Method basis-set "#BS" "E[Ha]" > performance.dat

for m in HF SVWN PBEPBE PBE1PBE 
do
	print
	for bs in STO-3G cc-pVDZ cc-pVTZ cc-pVQZ 
	do 
		mkdir -p $m/$bs
		cat <<EOF >> $m/$bs/input.com

%nproc=4
%mem=400MB
# METHOD BS
# sp scf=tight 

test calculations for H 

0 2
H 0.0 0.0 0.0 

EOF
sed -i "s/METHOD/$m/g" $m/$bs/input.com
sed -i "s/BS/$bs/g"    $m/$bs/input.com 
cd $m/$bs
echo "Running :" $m "in" $bs "basis set"
g16 input.com > input.log 
E=`grep Done input.log | awk '{printf "%12.8f", $5}'` 
nbs=`grep "basis functions, " input.log | awk '{printf "%5g", $1}'`
cd ../.. 
printf "%10s%10s%10d%12.8f\n" $m $bs $nbs $E >> performance.dat
done
done 


