%nproc=4
%mem=400MB
# b3lyp/6-31g(d) opt=moderedundant NMR

 Acetamide GS1

0 1
C1        -3.72909        3.14916        5.74294
C2        -3.45892        3.42021        4.29375
H1        -4.78035        2.81594        5.87024
H2        -3.56536        4.07554        6.33235
H3        -3.05298        2.35586        6.12764
O1        -2.58727        2.79338        3.71059
N1        -4.17562        4.35526        3.62943
H4        -5.09624        4.12369        3.22818
H5        -3.81027        5.31243        3.51561

D O1 C2 N1 H4 S 180 5.000000