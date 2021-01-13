%nproc=2
%mem=800MB
# PBE1PBE 6-311+g(d,p)
# scan scf=tight

Scan of HCl bond length

0 1
H
Cl 1 dist

dist <start> <steps> <step-size>
