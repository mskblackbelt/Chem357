%nproc=4
%mem=400MB
# MP2 def2tzvp
# sp scf=tight 

template file

0 1
Cl(Iso=37)	0.0 	0.0 	0.0
H(Iso=2)	0.0	0.0 	0.80

