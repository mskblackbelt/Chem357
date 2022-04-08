import re, os
import numpy as np
import sys
from  optparse import OptionParser
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter, FormatStrFormatter

NA=6.022*10**23

def list_callback(option, opt, value, parser):
     setattr(parser.values, option.dest, value.split(','))

parser = OptionParser()
parser.add_option('-p', '--normal_mode',  type='string', action='callback',  callback=list_callback,
                  help="list of normal modes used to generate inputs")
parser.add_option('-g', '--grid'       ,  type=int, action='store', help="number of grid points along the coordinate")
parser.add_option('-s', '--step_size'  ,  type=float, default=0.02, action='store', help="grid_spacing")
parser.add_option('-v', '--potential'  ,  type='string', action='store', help="potential to use")
parser.add_option('-r', '--rmass'      ,  type=float   , action='store', help="reduced mass")

opts, args = parser.parse_args()


Energy = np.load('pot_p'+opts.normal_mode[0]+'.npy')
harm_pot = np.load('pot_p'+opts.normal_mode[0]+'_harm.npy')


f=open('config.tmp', 'r')
cnfg_tmp = f.read()
f.close

cnfg_tmp = re.sub('potential_path', opts.potential, cnfg_tmp)
cnfg_tmp = re.sub('ngridx'        , str(opts.grid), cnfg_tmp) 
cnfg_tmp = re.sub('xmin'          , str(-(opts.grid-1)/2*opts.step_size*1.887*opts.rmass), cnfg_tmp)
cnfg_tmp = re.sub('xmax'          , str( (opts.grid-1)/2*opts.step_size*1.887*opts.rmass), cnfg_tmp)
cnfg_tmp = re.sub('output'        , 'p'+opts.normal_mode[0]+'.dat', cnfg_tmp)

out = open('config-dvr.cfg','w')
out.write(cnfg_tmp)
out.close()

os.system('python NuSol.py config-dvr.cfg')




fig, axes = plt.subplots(1,figsize=(6,6)) 
xaxis = np.linspace(0, opts.grid-1, opts.grid)
axes.plot(xaxis, Energy*2625.5, 'b', label='Real potential') 
axes.plot(xaxis, harm_pot*2625.5, 'g', label='Harmonic potential')

axes.set_xlim(-1, opts.grid)
axes.set_xticks(np.linspace(0, opts.grid-1, opts.grid))
axes.set_xticklabels([x*opts.step_size for x in range(-(opts.grid-1)/2, (opts.grid-1)/2+1)], fontsize='8')
axes.set_xlabel(r'Displacement along the coordinate', fontsize='10')

ymin=0 ; ymax= 100  #(int(np.amax(Energy)/100)+1)*100
axes.set_ylim(0,ymax)
yaxis=np.linspace(0,ymax,6)
axes.set_yticks(yaxis)
axes.set_yticklabels(yaxis)
axes.set_yticklabels(yaxis, fontsize='8')
axes.set_ylabel(r'Relative Energy [kJ/mol]', fontsize='10')


axes.tick_params(axis='both', which='both', bottom=True, top=True, labelbottom=True, right=True, left=True, labelleft=True)
for s in ['top', 'right', 'left', 'bottom']:
        axes.spines[s].set_visible(True)
axes.xaxis.set_tick_params(direction='out')
axes.yaxis.set_tick_params(direction='out')
axes.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

Eval = np.genfromtxt('eval_p'+opts.normal_mode[0]+'.dat')
Evec = np.genfromtxt('evec_p'+opts.normal_mode[0]+'.dat', skip_header=1)

for i in range(5): 
    axes.plot(xaxis, Evec[i,:]*5+Eval[i]*2625.5, 'y')
    #print np.ones((1,opts.grid))*Eval[i]*2625.5
    #axes.fill_between(xaxis, Evec[i,:]*5+Eval[i]*2625.5, np.ones((opts.grid,))*Eval[i]*2625.5, 'y')
    #axes.fill_between(xaxis, Eval*2625.5, Evec[i,:]*5+Eval[i]*2625.5,  'y')
fig.legend()
fig.tight_layout()
fig.savefig('1d_p'+opts.normal_mode[0]+'-estates.png')



    
        
        


