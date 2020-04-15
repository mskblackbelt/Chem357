import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter, FormatStrFormatter
import re

#Free= np.genfromtxt('diF_free.dat', skip_header=1, usecols=(1,2,3,4))
#En  = np.genfromtxt('diF_En.dat'  , skip_header=1, usecols=(1,2,3,4))
#Vib = np.genfromtxt('diF_Svib.dat', skip_header=1, usecols=(1,2,3,4))


En = []
ZPE= []
for n, conf in enumerate([ 'conf_01', 'conf_02', 'conf_03']) :
   for line in file(conf+'/input.log', 'r').readlines():
        if  re.search('SCF Done',   line): en = float(line.split()[4])
        if  re.search('Sum of electronic and zero-point Energies',   line): zpe = float(line.split()[6])
   En.append(en) ; ZPE.append(zpe)
En = np.array(En) ; ZPE = np.array(ZPE)
        
Ha2kcal =  627.5095
Ha2kJ   = 2625.5002

En*=Ha2kJ ; ZPE*=Ha2kJ
En[:] -= En[1]
ZPE[:]  -= ZPE[1]

color2= ['#1b9e77',
         '#d95f02',
         '#7570b3',
         '#e7298a']
color = ['#d7191c','#fdae61','#abd9e9','#2c7bb6']


params = {'mathtext.default': 'regular' }
plt.rcParams.update(params)

fig, axes = plt.subplots(1,1,figsize=(4,6))


print "%28s%20s\n" %('En [kJ/mol]', 'En+ZPE [kJ/mol]'),
for e, zpe, n   in zip(En, ZPE, range(1,4)):
   print "conf_%02g:%20.2f%20.2f\n" %(n, e, zpe),


for e in range(En.shape[0]):
   axes.plot([25,75], [En[e], En[e]], color=color[e], lw=3)
   axes.plot([75,125], [En[e],ZPE[e]], 'k--', lw=1)
   axes.plot([125,175], [ZPE[e], ZPE[e]], color = color[e], lw=3)
#   axes.plot(Temp+150, Free_corr[:,e], color = color[e], lw=2, linestyle=';')


axes.set_xlim(0,200)
axes.set_xticks([50,150])
axes.set_xticklabels(['Energy', '+ZPE' ])

axes.set_ylim(-10,20)
yaxis=np.linspace(-10,20,7)
axes.set_yticks(yaxis)
axes.set_yticklabels(yaxis)

axes.set_yticklabels(yaxis, fontsize='12')
axes.tick_params(axis='both', which='both', bottom=True, top=False, labelbottom=True, right=False, left=True, labelleft=True)
for s in ['top', 'right', 'left', 'bottom']:
        axes.spines[s].set_visible(False)
axes.xaxis.set_tick_params(direction='out')
axes.yaxis.set_tick_params(direction='out')
axes.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
axes.plot([1,1], [-10,20], 'k', lw=1.0)
axes.set_ylabel(r'Relative Energy [kJ/mol]', fontsize=12)

fig.legend()
fig.tight_layout()
fig.savefig('ZPE.png', dpi=200)
#fig.savefig('ZPE.pdf', dpi=200)
