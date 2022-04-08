
%nproc=4
%mem=400MB
# PBE1PBE cc-pVTZ
# sp scf=tight 

test calculations for H 

0 2
H 0.0 0.0 0.0 

