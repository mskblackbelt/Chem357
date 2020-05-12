# P. Chem. computational lab

- Assume knowledge of shell
- Create working folder for lab (Lab 3, Comp Chem, *etc.*)
- `git clone` repository containing input files, Jupyter notebook?

## Part I ##

- H atom (I)
  - Input file
    - Provide sample in Github?
  - System energy

## Part II ##

- HF molecule
  - Create input file by copying, modifying H atom file
  - Need to place atoms on *z-*axis (x, y = 0.0), z is variable (`Dist`)
  - Run script (provided) to make calculations varying distance. Check limits
  - Can have script run a couple of different basis sets and methods
  - Method performance
    - hf
    - pw-lda
    - pbe
    - pbe0
  - Basis sets
    - 6-31g
    - def2tzvp
    - Others?
  - Compute atomization energy… need to compute energies for H and F separately (H already done…)
  - Plot bond lengths, estimate minimum (matplotlib)

## Alternate Part II (HF probably better) ##

- Molecular oxygen (III)
  - Provide `xyz` file? Have them create one?
  - Set up calculation but leave `spin` empty (possible in Gaussian?)
  - Check filling of orbitals… reasonable?
  - Using pbe and pbe0, calculate the binding curve in the interval [0.8, 1.6] Å with a stepwidth of 0.1 Å as before. Also, calculate the atomization energy (∆H~at~).
  - Repeat the calculation with `spin collinear` and `default_initial_moment 2.0` -- is Hund’s rule now fulfilled? Compare the results: Do both spin settings yield the same equilibrium bond length? Calculate the difference in the total energy at the equilibrium bond length. Which one is lower? How does it compare to the experimental value of 1.21 Å? How does the atomization energy (∆H~at~) compare to the experimental value of 5.18 eV?
 

## Part III (long, but only 2D plotting)##

- Planar/Pyramidal H~3~O^+^ (IV-VIII)

## Alternate Part III ##
 
- Visualizing density differences in *para-*benzoquinone (IX)
  - Need to visualize *cube* outputs from Gaussian (Python packages [`openchemistry`](https://blog.kitware.com/open-chemistry-avogadro-electronic-structure-in-jupyterlab/), [`pygauss`](https://pypi.org/project/pygauss/) and [`exatomic`](https://github.com/exa-analytics/exatomic))
  - Provide `xyz` file for students in repo


## Getting Part III to work with CClib/OpenChemistry

### CJSON structure

- 'chemicalJson' (or 'chemical json'): **required**, 1 or 0 (new version vs. old, camelCase or spaces in keys)
- 'atoms': **required**

### OpenChemistry _molecule.Molecule structure

- orbitals
- structure
- properties
- vibrations

OpenChemistry CJSON files expect the following for vibrational data: 

- Seems to take only IR _or_ Raman data? Caffeine molecule only has one set of vibrational data
- Four categories: 
  - 'frequencies': 
      frequency of each mode
  - 'intensities': 
      intensity of each mode
  - 'modes':
      numeric identifier for the mode
  - 'eigenVectors': 
      array of eigenvectors for each vibration
      
Gaussian16 outputs (from cclib import)

- 'displacement' => 'eigenVectors' (need reshape?)
- 'frequencies' == 'frequencies'
- 'intensities' == 'intensities'
- 'vibration symmetry' : not needed

Need to add a column for modes. Frequencies are already ordered from lowest to highest, just need to add a column (range(1,len(col)))
