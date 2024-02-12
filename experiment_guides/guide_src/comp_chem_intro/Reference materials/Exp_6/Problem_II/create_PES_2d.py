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
parser.add_option('-g', '--grid'       ,  type='string', action='callback',  callback=list_callback,
                  help="number of grid points along the coordinate")
parser.add_option('-s', '--step_size'  ,  type='string', action='callback',  callback=list_callback,
                  help="grid_spacing")
parser.add_option('-c', '--compute'    ,  type=int , default=0, action='store', 
                  help="initialize computations")

opts, args = parser.parse_args()


f=open('input.template','r')
control_tmp = f.read()
f.close()

atom = []; xyz = []
for line in file('conf_01.xyz', 'r').readlines()[2:]:
     atom.append( line.split()[0])
     xyz.append( map(float, line.split()[1:]) ) 
xyz = np.array(xyz)

dim = len(opts.normal_mode)

modes = [] ; modes_data = []
for i in opts.normal_mode: 
    modes.append(np.genfromtxt('conf_01-vib_modes/mode_'+i+'.dat',skip_header=1))
    modes_data.append( map(float, file('conf_01-vib_modes/mode_'+i+'.dat', 'r').readlines()[0].split()[2::3]) )
    #print modes_data


if dim == 1: 
    step_size=float(opts.step_size[0]) ; grid = int(opts.grid[0])
    if os.access('PES_1D', os.F_OK): pass
    else:  os.mkdir('PES_1D')
    Energy = []; harm_pot = []
    geom = file('PES_1D/geometry_p'+opts.normal_mode[0]+'.xyz', 'w')
    for i in range(-(grid-1)/2, (grid-1)/2+1):
        dir_name = 'PES_1D/normal_mode_p'+opts.normal_mode[0]+'_grid_i%02s' % (str(i+(grid-1)/2).zfill(2))
        if os.access(dir_name, os.F_OK): pass
        else:  os.mkdir(dir_name)
        out=open(dir_name+'/input.com', 'w')
        out.write(control_tmp)
        new_geom = xyz[:] +i*modes[0]*modes_data[0][3]**(1./2)*step_size
        print >> geom, "%3d\n" %(len(atom)),
        print >> geom, "step %3d\n" %(i), 
        for at in range(len(atom)): 
                  print >> out, "%3s%12.6f%12.6f%12.6f\n"  %(atom[at], new_geom[at,0], new_geom[at,1], new_geom[at,2]),
                  print >> geom,"%3s%12.6f%12.6f%12.6f\n"  %(atom[at], new_geom[at,0], new_geom[at,1], new_geom[at,2]),
        print >> out, "\n", 
        out.close()
        if opts.compute == 1: 
            print "Running system: %s" %(dir_name)
            os.system('g16 '+ dir_name+'/input.com')
        for line in file(dir_name+'/input.log', 'r'): 
            if  re.search('SCF Done',   line): en = float(line.split()[4]) 
        Energy.append(en)
        harm_pot.append((modes_data[0][2]*modes_data[0][3]*(i*step_size)**2)/2*(10**(-21)*NA))
    geom.close()
        
        #print harm_pot[-1]

    Energy = np.array(Energy) ; harm_pot = np.array(harm_pot)
    Energy -= np.amin(Energy)
    np.save('pot_p'+opts.normal_mode[0]+'.npy', Energy)
    np.save('pot_p'+opts.normal_mode[0]+'_harm.npy', harm_pot/2625.5002)
    Energy *= 2625.5002
    
    f=file('pot_p'+opts.normal_mode[0]+'.dat', 'w')
    for i, e, h in zip(range(-(grid-1)/2, (grid-1)/2+1), Energy, harm_pot): 
            print >> f, "%3d%12.6f%12.6f\n" %(i, e, h),
    f.close()
    
    fig, axes = plt.subplots(1,figsize=(6,6)) 
    xaxis = np.linspace(0, grid-1, grid)
    axes.plot(xaxis, Energy, 'b', label='Real potential') 
    axes.plot(xaxis, harm_pot, 'g', label='Harmonic potential')
    
    axes.set_xlim(-1, grid)
    axes.set_xticks(np.linspace(0, grid-1, grid))
    axes.set_xticklabels([x*step_size for x in range(-(grid-1)/2, (grid-1)/2+1)], fontsize='8')
    axes.set_xlabel(r'Displacement along the normal mode', fontsize='10')
    
    ymin=0 ; ymax=100 #(int(np.amax(Energy)/100)+1)*100
    axes.set_ylim(0,ymax)
    yaxis=np.linspace(0,ymax,6)
    axes.set_yticks(yaxis)
    axes.set_yticklabels(yaxis)
    axes.set_yticklabels(yaxis, fontsize='10')
    axes.set_ylabel(r'Relative Energy [kJ/mol]', fontsize='10')
    
    
    axes.tick_params(axis='both', which='both', bottom=True, top=True, labelbottom=True, right=True, left=True, labelleft=True)
    for s in ['top', 'right', 'left', 'bottom']:
            axes.spines[s].set_visible(True)
    axes.xaxis.set_tick_params(direction='out')
    axes.yaxis.set_tick_params(direction='out')
    axes.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    
    #axes.plot([1,1], [-10,20], 'k', lw=1.0)
    
    fig.legend() 
    fig.tight_layout()
    fig.savefig('1d_p'+opts.normal_mode[0]+'.png')



elif dim == 2:
    i_step_size=float(opts.step_size[0]) ; j_step_size = float(opts.step_size[1])
    i_grid     = int(opts.grid[0])      ; j_grid      = int(opts.grid[1])
    if os.access('PES_2D', os.F_OK): pass
    else:  os.mkdir('PES_2D')
    geom = file('PES_2D/geometry_p'+opts.normal_mode[0]+'_r'+opts.normal_mode[1]+'.xyz', 'w')
    for i in range(-(i_grid-1)/2, (i_grid-1)/2+1):
      for j in range(-(j_grid-1)/2, (j_grid-1)/2+1):
        dir_name = 'PES_2D/normal_mode_p'+opts.normal_mode[0]+'_grid_i%02s_j%02s' % (str(i+(i_grid-1)/2).zfill(2), str(j+(j_grid-1)/2).zfill(2))
        if os.access(dir_name, os.F_OK): pass
        else:  os.mkdir(dir_name)
        out=open(dir_name+'/input.com', 'w')
        out.write(control_tmp)
        new_geom = xyz[:] +i*modes[0]*modes_data[0][3]**(1./2)*i_step_size+j*modes[1]*modes_data[1][3]**(1./2)*j_step_size
        print >> geom, "%3d\n" %(len(atom)),
        print >> geom, "step %3d\n" %(i), 
        for at in range(len(atom)): 
                  print >> out, "%3s%12.6f%12.6f%12.6f\n"  %(atom[at], new_geom[at,0], new_geom[at,1], new_geom[at,2]),
                  print >> geom,"%3s%12.6f%12.6f%12.6f\n"  %(atom[at], new_geom[at,0], new_geom[at,1], new_geom[at,2]),
        print >> out, "\n", 
        out.close()
        #if opts.compute == 1: 
        #    print "Running system: %s" %(dir_name)
        #    os.system('g16 '+ dir_name+'/input.com')
        #for line in file(dir_name+'/input.log', 'r'): 
        #    if  re.search('SCF Done',   line): en = float(line.split()[4]) 
        #Energy.append(en)
        #harm_pot.append((modes_data[0][2]*modes_data[0][3]*(i*step_size)**2)/2*(10**(-21)*NA))
    geom.close()

    
        
        



