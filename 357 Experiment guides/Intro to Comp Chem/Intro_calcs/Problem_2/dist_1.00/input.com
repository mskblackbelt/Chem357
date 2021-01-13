%nproc=4
%mem=400MB
# HF 6-31G(d,p)
# sp scf=tight

template file

0 1
F 0.0 0.0 0.0 
H 0.0 0.0 1.00

