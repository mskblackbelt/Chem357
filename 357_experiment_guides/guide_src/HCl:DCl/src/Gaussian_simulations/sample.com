%nproc=2
%mem=800MB
# MP2 def2qzvpp
# opt freq=(anharm,vibrot) scf=tight

<title information>

<charge> <multiplicity>
<atom1>(Iso=<mass_num>) 	<x1>	<y1>	<z1>
<atom2>(Iso=<mass_num>) 	<x2>	<y2>	<z2>
<empty line>

