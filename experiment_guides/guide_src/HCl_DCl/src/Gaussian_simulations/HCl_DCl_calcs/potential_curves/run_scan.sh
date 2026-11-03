#!/bin/bash

# A simple script to populate directory tree with 
# instances of input.temp file with substituted DIST variable

# Created by MM / NYC Feb 2019


# Coarse-grained calculations for overall shape of the curve.
# Sets up and runs calcs for bond lengths from 0.7 to 1.3 Angstrom
# in 0.2 Angstrom steps.
for d in `seq -f "%3.2f" 0.7 0.1 1.3`
do 
	echo "running position " $d
	mkdir dist_$d 
	sed -e "s/DIST/$d/g" input.temp > dist_$d/input.com 
	cd dist_$d
	g16 input.com > input.log
	cd ../
done

# Fine-grained calculations to give definition to the base of the well.
# Sets up and runs calcs for bond lengths from 0.85 to 0.95 Angstrom
# in 0.02 Angstrom steps.

for d in `seq -f "%3.2f" 0.85 0.02 0.95`
do 
	echo "running position " $d
	mkdir dist_$d 
	sed -e "s/DIST/$d/g" input.temp > dist_$d/input.com 
	cd dist_$d
	g16 input.com > input.log
	cd ../
done

# Create a file to concatenate a table of distance and energy values
printf "%5s%12s\n" dist "E[Ha]" > dist_E.dat

# Pull calculated energy values from each output file and append 
# the distance and calculated energy to the data table.
for i in dist_[01]* 
	do 
	d=`echo $i | awk -F"_" '{print $2}'`
	E=`grep "Done" $i/input.log | awk '{printf "%20.8f", $5}'`
        printf "%5.2f%20.8f\n" $d $E >> dist_E.dat 
done



