# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.23.8",
#     "matplotlib>=3.10.9",
#     "numpy>=2.4.6",
#     "openai>=2.38.0",
#     "pydantic-ai>=1.104.0",
#     "scipy>=1.17.1",
# ]
# ///

import marimo

__generated_with = "0.23.8"
app = marimo.App()


@app.cell
def _():
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.constants import c, h, k, e 
    from scipy import stats
    # Import speed_of_light, Planck, Boltzmann and elementary charge constants
    # Spectroscopic constants for the molecule (example values for a diatomic molecule)
    B_e = 10.59341
    alpha_e = 0.30718
    D_J = 0.00053149
    weXe = 52.8186
    w_e = 2990.946
    return B_e, D_J, alpha_e, c, e, h, k, np, plt, stats, w_e, weXe


@app.cell
def _(np):
    v_max, j_max = 2, 10
    v_vals = np.arange(v_max)
    j_vals = np.arange(j_max)
    temp = 298
    peak_width = 1.5
    return j_max, j_vals, peak_width, temp


@app.cell
def _(B_e, D_J, alpha_e, c, h, j_vals, k, np, temp, w_e, weXe):
    def rotEnergy(_v, J):
        return h * c * 100 * (B_e * J * (J + 1) - alpha_e * (_v + 1 / 2) * J * (J + 1) - D_J * J ** 2 * (J + 1) ** 2)

    def rovibEnergy(_v, J):
        return h * c * 100 * (w_e * (_v + 1 / 2) - weXe * (_v + 1 / 2) ** 2 + B_e * J * (J + 1) - D_J * J ** 2 * (J + 1) ** 2 - alpha_e * (_v + 1 / 2) * J * (J + 1))

    def deltaE_Rbranch(J):
        return rovibEnergy(1, J + 1) - rovibEnergy(0, J)

    def deltaE_Pbranch(J):
        return rovibEnergy(1, J - 1) - rovibEnergy(0, J)

    def Qrot(_v, temp=temp):
        return np.sum((2 * j_vals + 1) * np.exp(-rotEnergy(_v, j_vals) / (k * temp)))

    def pop(_v, J, temp=temp):
        return np.exp(-rotEnergy(_v, J) / (k * temp)) / Qrot(_v, temp)

    return Qrot, pop, rotEnergy, rovibEnergy


@app.cell
def _(
    B_e,
    D_J,
    alpha_e,
    j_max,
    j_vals,
    np,
    peak_width,
    plt,
    pop,
    stats,
    temp,
    w_e,
    weXe,
):
    def vibrot_wn(_v, J):
        return w_e * (_v + 1 / 2) - weXe * (_v + 1 / 2) ** 2 + B_e * J * (J + 1) - D_J * J ** 2 * (J + 1) ** 2 - alpha_e * (_v + 1 / 2) * J * (J + 1)

    def Pbranch_vals(_v, J, temp=temp):
        return vibrot_wn(_v + 1, J - 1) - vibrot_wn(_v, J)

    def Rbranch_vals(_v, J, temp=temp):
        return vibrot_wn(_v + 1, J + 1) - vibrot_wn(_v, J)

    def wn_vals(temp=298, _v=0, step=0.1):
        return np.arange(Pbranch_vals(_v, np.arange(j_max + 1), temp).min(), Rbranch_vals(_v, np.arange(j_max), temp).max(), step)

    def _branch_spectrum(_v, branch_vals_fn, j_start, degeneracy_offset, temp=temp, peak_width=peak_width):
        """
        Generalized branch spectrum calculator.

        Args:
            branch_vals_fn: Callable returning line positions (e.g. Pbranch_vals or Rbranch_vals)
            j_start: Starting J value (1 for P-branch, 0 for R-branch)
            degeneracy_offset: Added to J for the intensity factor (0 for P, 1 for R)
        """
        j_vals = np.arange(j_start, j_max - (1 - j_start), 1)  # preserves original ranges
        wn = wn_vals(temp)

        # Shape: (len(j_vals), len(wn))
        locs = np.array([branch_vals_fn(_v, j, temp) for j in j_vals])
        populations = np.array([pop(_v, j, temp) for j in j_vals])
        degeneracy = (j_vals + degeneracy_offset)[:, np.newaxis]

        gaussians = stats.norm.pdf(wn, loc=locs[:, np.newaxis], scale=peak_width)
        return np.sum(degeneracy * populations[:, np.newaxis] * gaussians * np.sqrt(2 * np.pi) * peak_width, axis=0)


    def Pbranch_spectrum(_v, temp=temp, peak_width=peak_width):
        return _branch_spectrum(_v, Pbranch_vals, j_start=1, 
                                degeneracy_offset=0, temp=temp, 
                                peak_width=peak_width)

    def Rbranch_spectrum(_v, temp=temp, peak_width=peak_width):
        return _branch_spectrum(_v, Rbranch_vals, j_start=0, 
                                degeneracy_offset=1, temp=temp, 
                                peak_width=peak_width)

    plt.plot(wn_vals(298), 
             np.sum([Pbranch_spectrum(0, 298, 2.5), 
                     Rbranch_spectrum(0, 298, 2.5)], axis=0), 'r-', 
             np.concatenate((Rbranch_vals(0, j_vals[:9], 298), 
                                   Pbranch_vals(0, j_vals[:10], 298))), 
             np.concatenate(((j_vals[:9] + 1) * pop(0, j_vals[:9], temp), 
                             j_vals[:10] * pop(0, j_vals[:10], temp))), 'b.')
    return (
        Pbranch_spectrum,
        Pbranch_vals,
        Rbranch_spectrum,
        Rbranch_vals,
        wn_vals,
    )


@app.cell
def _(e, rovibEnergy):
    leveldiagram_lines = []
    for _v in range(2):
        leveldiagram_lines.append([])
        for J in range(10):
            leveldiagram_lines[_v].append(rovibEnergy(_v, J) / e)
    return (leveldiagram_lines,)


@app.cell
def _(j_max, np):
    levels = [np.arange(j_max), np.arange(j_max)]
    return (levels,)


@app.cell
def _(
    Pbranch_spectrum,
    Pbranch_vals,
    Rbranch_spectrum,
    Rbranch_vals,
    j_vals,
    leveldiagram_lines,
    levels,
    np,
    pop,
    wn_vals,
):
    # Export the data drawn by vibrot_energy_diagram.tikz (pgfplots, built by Tectonic).
    # The figure itself is drawn in TikZ, so no LaTeX installation is needed here.
    import marimo as mo

    _out = mo.notebook_dir() / 'vibrot_data'
    _out.mkdir(exist_ok=True)
    _wn = wn_vals(298)
    _xmin, _xmax = _wn.min() - 15, _wn.max() + 45
    _x_start, _x_end = Pbranch_vals(0, 9) - 15, Rbranch_vals(0, 8) + 15

    # Axis limits and level-line extent, as TeX macros
    (_out / 'params.tex').write_text(
        f'\\def\\vrXmin{{{_xmin:.4f}}}\n'
        f'\\def\\vrXmax{{{_xmax:.4f}}}\n'
    )

    # Energy levels as line segments separated by "nan" rows (pgfplots jumps)
    _rows = ['x,E']
    for _v in [0, 1]:
        for _j in levels[_v]:
            _E = leveldiagram_lines[_v][_j]
            _rows += [f'{_x_start:.4f},{_E:.6f}', f'{_x_end:.4f},{_E:.6f}', 'nan,nan']
    (_out / 'levels.csv').write_text('\n'.join(_rows) + '\n')

    # One row per labelled level: J value and energy (eV)
    _rows = ['v,J,E']
    for _v in [0, 1]:
        for _j in levels[_v]:
            _rows.append(f'{_v},{_j},{leveldiagram_lines[_v][_j]:.6f}')
    (_out / 'level_labels.csv').write_text('\n'.join(_rows) + '\n')

    # Transitions: wavenumber, lower and upper level energies (eV), and peak height
    _rows = ['branch,J,wn,Elow,Ehigh,height']
    for _j in levels[0][1:]:
        _rows.append(f'P,{_j},{Pbranch_vals(0, _j):.4f},{leveldiagram_lines[0][_j]:.6f},'
                     f'{leveldiagram_lines[1][_j - 1]:.6f},{j_vals[_j] * pop(0, j_vals[_j]):.6f}')
    for _j in levels[1][:-1]:
        _rows.append(f'R,{_j},{Rbranch_vals(0, _j):.4f},{leveldiagram_lines[0][_j]:.6f},'
                     f'{leveldiagram_lines[1][_j + 1]:.6f},{(j_vals[_j] + 1) * pop(0, j_vals[_j]):.6f}')
    (_out / 'transitions.csv').write_text('\n'.join(_rows) + '\n')

    # Simulated spectrum (every other point of the 0.1 cm^-1 grid)
    _peak_width = 2.5
    _absorb = np.sum([Pbranch_spectrum(0, peak_width=_peak_width),
                      Rbranch_spectrum(0, peak_width=_peak_width)], axis=0)
    _rows = ['wn,A'] + [f'{_x:.2f},{_y:.6f}' for _x, _y in zip(_wn[::2], _absorb[::2])]
    (_out / 'spectrum.csv').write_text('\n'.join(_rows) + '\n')
    return


if __name__ == "__main__":
    app.run()
