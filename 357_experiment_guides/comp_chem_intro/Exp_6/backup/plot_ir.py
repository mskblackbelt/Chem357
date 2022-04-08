import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import sys
from  optparse import OptionParser

scaling_factor=0.965
broaden = 3
EXP = np.genfromtxt('experimental.dat')
xmin= 400 ; xmax=2000
fig, ax = plt.subplots(1, figsize=(8, 4))

parser = OptionParser()
parser.add_option("-a", "--formic_acid", action='store', default=None,
                  help="C=O mode of the formic acid")
parser.add_option("-b", "--formate"    , action='store', default=None,
                  help="COO as of the formate")
parser.add_option('-p', "--print_mode", action='store', type=int, default=0, 
                  help="normal mode vectors to be printed out")

opts, args = parser.parse_args()

ax.tick_params(axis='both', which='both', bottom=True, top=False, labelbottom=True, right=False, left=False, labelleft=False)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False);  ax.spines['left'].set_visible(False)
ax.xaxis.set_tick_params(direction='out')
ax.yaxis.set_major_formatter(NullFormatter())
ax.set_ylim(0,5) ; ax.set_xlim(xmin, xmax)
xticks = np.linspace(xmin,xmax,int((xmax-xmin)/200)+1)
ax.set_xticks(xticks[:-1])
ax.set_xticklabels([int(x) for x in xticks[:-1]], fontsize=12)
ax.set_xlabel('Wavelength [cm-1]')

IR = []
Int = []

def gaussian(X,x0,s):
    return np.exp(-0.5*((X-x0)/s)**2)

for n, conf in enumerate([ 'conf_01', 'conf_02', 'conf_03']) :
    freq = [] ; ints = [] ; red_mass = [] ; fc_const = [] ; vibs = []
    normal_mode_flag=False
    for line in file(conf+'/input.log', 'r').readlines():

       if re.search('^ Frequencies', line):
                    freq_line = line.strip()
                    for f in freq_line.split()[2:5]: freq.append(float(f))
                    normal_mode_flag = False

       elif re.search('^ IR Inten', line):
                    ir_line = line.strip()
                    for i in ir_line.split()[3:6]: ints.append(float(i))

       elif re.search('^ Frc consts', line):
                    fc_line = line.strip()
                    for i in fc_line.split()[3:6]: fc_const.append(float(i))

       elif re.search('^ Red. masses', line):
                    rm_line = line.strip()
                    for i in rm_line.split()[3:6]: red_mass.append(float(i))

       elif re.search('^  Atom  AN', line):
                    normal_mode_flag = True          #locating normal modes of a frequency
                    mode_1 = []; mode_2 = []; mode_3 = []
                    continue

       elif normal_mode_flag == True and re.search('^\s*.\d\s\s\s\d', line):
                    mode_1.append(map(float, line.split()[2:5]))
                    mode_2.append(map(float, line.split()[5:8]))
                    mode_3.append(map(float, line.split()[8:11]))

       elif normal_mode_flag == True:
                   normal_mode_flag = False
                   for m in [mode_1, mode_2, mode_3]: vibs.append(np.array(m))

    data = np.zeros( (len(freq), 2) )
    for c, ir, i  in zip(range(len(freq)), freq, ints):
        data[c,0] = ir; data[c,1]=i


    Ytot = np.zeros((4001,))
    X=np.linspace(0, 4000,4001)
    Y=np.zeros((4001,))
    for l in range(data.shape[0]):
        Y = data[l,1]*gaussian(X, data[l,0], broaden)
        Ytot += Y

    shift=1.2*n+0.2
    scale_t  =  1./np.amax(Ytot[xmin:xmax+100])

    Xsc = X*scaling_factor
    Ysc = Ytot*scale_t

    ir_theo = ax.plot(Xsc, Ysc+shift, color='0.25', linewidth=1)
    ax.fill_between(Xsc, np.linspace(shift, shift, len(Ysc)), Ysc+shift, color='0.5', alpha=0.5)
    ax.text(1850, shift+0.05, conf)
    #ax.plot([xmin,xmax], [shift, shift], 'k', lw=1)

    if opts.print_mode != 0 and conf == 'conf_01': 
        #print freq, ints, red_mass
        f = file('mode_'+str(opts.print_mode)+'.dat', 'w')
        print >> f, "Freq = %12.2f Int = %12.6f force_const = %12.6f red_mass = %12.6f \n" %( freq[opts.print_mode-1], ints[opts.print_mode-1], fc_const[opts.print_mode-1], red_mass[opts.print_mode-1]),
        for i in range(vibs[0].shape[0]):
            print >> f, "%12.6f%12.6f%12.6f\n" %(vibs[opts.print_mode-1][i , 0], vibs[opts.print_mode-1][i, 1], vibs[opts.print_mode-1][i, 2]),
        f.close()


shift=3.8

scale_exp=  1./np.amax(EXP[:,1])
ax.plot(EXP[:,0], EXP[:,1]*scale_exp+shift, color='r', alpha=0.5, linewidth=2)
ax.fill_between(EXP[:,0], EXP[:,1]*scale_exp+shift, np.linspace(shift,shift, len(EXP[:,1])), color='r', alpha=0.25)
ax.text(1800, shift+0.05, 'experimental')

hpar = 605
ax.plot([hpar, hpar], [0,5], 'k--')
ax.text(hpar+10, 4.8, r'$\nu_{||}$', fontsize=8)

if opts.formic_acid != None:
    fa=float(opts.formic_acid)*scaling_factor
    ax.plot([fa, fa], [0, 5], 'b--')
    ax.text(fa+10, 4.8, r'$\nu$(C=O)', fontsize=8)

if opts.formate     != None:
    fb=float(opts.formate)*scaling_factor
    ax.plot([fb, fb], [0, 5], 'g--')
    ax.text(fb+10, 4.8, r'$\nu$(COO)$_{as}^-$', fontsize=8)

fig.tight_layout()
plt.savefig('ir.png', dpi=200)



