%nproc=4
%mem=400MB
# HF 6-31G(d,p)
# opt freq scf=tight

Planar H3O+ vibrational analysis

1 1
O  0.00  0.00  0.00
H  0.92 -0.53  0.00
H -0.92 -0.52  0.00
H  0.00	 1.06  0.00

