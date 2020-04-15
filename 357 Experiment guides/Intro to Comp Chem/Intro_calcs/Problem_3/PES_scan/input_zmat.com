%nproc=4
%mem=400MB
# MP2 6-31G(d,p) scf=tight scan

h3o+ scan along umbrella mode

1 1
O 
X 1 a 
H 1 a 2 HOX
H 1 a 2 HOX 3  120.
H 1 a 2 HOX 3 -120.

a=0.961
HOX 135. 45 -1.

