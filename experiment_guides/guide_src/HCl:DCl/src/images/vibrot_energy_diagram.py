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
    import matplotlib as mpl
    from scipy.constants import c, h, k, e 
    from scipy import stats
    # Import speed_of_light, Planck, Boltzmann and elementary charge constants
    # Spectroscopic constants for the molecule (example values for a diatomic molecule)
    B_e = 10.59341
    alpha_e = 0.30718
    D_J = 0.00053149
    weXe = 52.8186
    w_e = 2990.946
    return B_e, D_J, alpha_e, c, e, h, k, mpl, np, plt, stats, w_e, weXe


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
def _(Qrot):
    print(Qrot(0, 298))
    return


@app.cell
def _(c, h, j_vals, rotEnergy):
    print(rotEnergy(0, j_vals)/(h*c*100))
    return


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
    from scipy import signal

    def wn_vals(temp=298, _v=0, step=0.1):
        return np.arange(Pbranch_vals(_v, np.arange(j_max + 1), temp).min(), Rbranch_vals(_v, np.arange(j_max), temp).max(), step)

    # def Pbranch_spectrum(_v, temp=temp):
    #     peaks = []
    #     j_vals = np.arange(1, j_max, 1)
    #     for n in range(len(j_vals)):
    #         peaks.append(j_vals[n] * pop(_v, j_vals[n], temp) * stats.norm.pdf(wn_vals(temp), loc=Pbranch_vals(_v, j_vals[n], temp), scale=peak_width) * np.sqrt(2 * np.pi) * peak_width)
    #     return np.sum(peaks, axis=0)

    # def Rbranch_spectrum(_v, temp=temp):
    #     peaks = []
    #     j_vals = np.arange(0, j_max - 1, 1)
    #     for n in range(len(j_vals)):
    #         peaks.append((j_vals[n] + 1) * pop(_v, j_vals[n], temp) * stats.norm.pdf(wn_vals(temp), loc=Rbranch_vals(_v, j_vals[n], temp), scale=peak_width) * np.sqrt(2 * np.pi) * peak_width)
    #     return np.sum(peaks, axis=0)
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

    print(len(signal.resample(pop(0, np.arange(j_max), 298), len(wn_vals(298)))))

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
def _(j_max, leveldiagram_lines, np):
    lvl_energies = [[],[]]
    levels = [[], []]

    for _v in [0, 1]:
        levels[_v] = np.arange(j_max)
        for _j in leveldiagram_lines[_v][:]:
            lvl_energies[_v].append(f'{_j:0.3f}')
    return (levels,)


@app.cell
def _(
    Pbranch_spectrum,
    Pbranch_vals,
    Rbranch_spectrum,
    Rbranch_vals,
    e,
    j_vals,
    leveldiagram_lines,
    levels,
    mpl,
    np,
    plt,
    pop,
    rovibEnergy,
    wn_vals,
):
    from matplotlib import gridspec
    from matplotlib.patches import ConnectionPatch

    mpl.rcParams.update({
        'pgf.texsystem': 'xelatex', 
        'font.family': 'serif', 
        "text.usetex": True, 
        "pgf.rcfonts": False, 
        'font.serif': ['STIX Two Text', 'Palatino'], 
        'axes.titlesize': 8, 
        'axes.labelsize': 8, 
        'xtick.labelsize': 6, 
        'ytick.labelsize': 6
    })

    # Generate the figure and subplots
    fig = plt.figure(figsize=(4, 6))
    plotted_js = np.arange(10)
    xmin, xmax = (wn_vals(298).min() - 15, wn_vals(298).max() + 45)
    gs0 = gridspec.GridSpec(2, 1, figure=fig, hspace=0.06, height_ratios=[4, 1])
    gs00 = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs0[0], hspace=0.03)
    gs01 = gridspec.GridSpecFromSubplotSpec(1, 1, subplot_spec=gs0[1])
    axs_trans = (fig.add_subplot(gs00[1]), fig.add_subplot(gs00[0]))
    ax_spec = fig.add_subplot(gs01[0])

    ## Energy level plot
    # Plotting the energy levels

    # Make the levels
    for v in [0, 1]:
        axs_trans[v].hlines(rovibEnergy(v, plotted_js) / e, 
                  Pbranch_vals(0, 9) - 15, 
                  Rbranch_vals(0, 8) + 15, 
                  colors='k', linewidth=0.75)
        axs_trans[v].set_xlim(xmin, xmax)

    # Adjust the vertical limits and add diagonal lines for y-axis break
    axs_trans[1].set_ylim(0.53, 0.66)
    axs_trans[0].set_ylim(0.172, 0.315)

    ax_kwargs = {
        'transform': axs_trans[1].transAxes, 
        'color':'k', 
        'clip_on':False
    }

    _d = 0.025 # Diagonal line length in axes coordinates
    axs_trans[1].plot((-_d, +_d), (-_d, +_d), **ax_kwargs)
    ax_kwargs.update(transform=axs_trans[0].transAxes)
    axs_trans[0].plot((-_d, +_d), (1 - _d, 1 + _d), **ax_kwargs)

    for ax in [axs_trans[0], axs_trans[1], ax_spec]:
        for _side in ['right', 'top']:
            ax.spines[_side].set_visible(False)
    axs_trans[1].spines['bottom'].set_visible(False)
    xtick_params = {
        'axis': 'x',
        'which': 'both', 
        'bottom': False, 
        'top': False, 
        'labelbottom': False, 
        'pad': 2
    }

    for v in [0, 1]:
        axs_trans[v].tick_params(**xtick_params)
        axs_trans[v].set_yticks([])

    jlbl_kwargs = {'fontsize': 6, 'ha': 'left', 'va': 'center'}

    for v in [0, 1]:
        for _j in levels[v]:
            axs_trans[v].text(3095, 
                    (leveldiagram_lines[v][_j] - (0.004 if _j == 0 else 0)), 
                    str(levels[v][_j]), 
                    **jlbl_kwargs)

    axs_trans[0].text(3064, leveldiagram_lines[0][9], "$J\\,''\\!=$", **jlbl_kwargs)
    axs_trans[1].text(3066, leveldiagram_lines[1][9], "$J\\,'\\!=$", **jlbl_kwargs)

    _arrow_styles = dict(
        arrowstyle='-|>', 
        linewidth=1.25
    )    

    _trans_kwargs = _arrow_styles | dict(
        coordsA='data', 
        coordsB='data', 
        axesA=axs_trans[0], 
        axesB=axs_trans[1]
    )

    color_p = (0.24, 0.35, 0.67)
    color_r = (0.19, 0.5, 0.08)

    for _j in levels[0][1:]:
        _x = Pbranch_vals(0, _j)
        _con = ConnectionPatch(xyA=(_x, leveldiagram_lines[0][_j]), 
                               xyB=(_x, leveldiagram_lines[1][_j - 1]), 
                               color=color_p, **_trans_kwargs)
        axs_trans[1].add_artist(_con)
    for _j in levels[1][:-1]:
        _x = Rbranch_vals(0, _j)
        _con = ConnectionPatch(xyA=(_x, leveldiagram_lines[0][_j]), 
                               xyB=(_x, leveldiagram_lines[1][_j + 1]), 
                               color=color_r, **_trans_kwargs)
        axs_trans[1].add_artist(_con)

    axs_trans[0].text(2645, leveldiagram_lines[0][5], "$v\\,''\\!=0$", rotation='vertical', fontsize=6)
    axs_trans[1].text(2645, leveldiagram_lines[1][5], "$v\\,'\\!=1$", rotation='vertical', fontsize=6)
    fig.text(0.05, 0.58, 'Energy (eV)', rotation='vertical', ha='center', va='center', fontsize=8)

    # Spectrum plot
    _peak_width = 2.5
    ax_spec.plot(wn_vals(298), 
                 np.sum([Pbranch_spectrum(0, peak_width=_peak_width), 
                         Rbranch_spectrum(0, peak_width=_peak_width)], axis=0), 
                 'k-', linewidth=1)
    ax_spec.set_ylim(-0.002, 0.2)
    ax_spec.set_xlim(xmin, xmax)
    ax_spec.set_ylabel('Absorbance')
    ax_spec.set_xlabel('Wavenumber (cm$^{-1}$)')
    ax_spec.set_yticks([])
    ax_spec.tick_params(pad=2)
    ax_spec.yaxis.set_label_coords(-0.081, 0.5)
    _length = 0.07
    _shrink = 3
    _arrow_kwargs = dict(
        ha='center', 
        rotation=90, 
        fontsize=6, 
    )
    _arrowprop_kwargs = _arrow_styles | dict(
        shrinkA=_shrink
    )
    for _j in levels[0][1:]:
        _x, _y = (Pbranch_vals(0, _j), j_vals[_j] * pop(0, j_vals[_j]))
        ax_spec.annotate(f'P({_j})', xy=(_x, _y), xytext=(_x, _y + _length), 
                         xycoords='data', textcoords='data', 
                         arrowprops=dict(color=color_p, **_arrowprop_kwargs), 
                         **_arrow_kwargs)
    for _j in levels[1][:-1]:
        _x, _y = (Rbranch_vals(0, _j), (j_vals[_j] + 1) * pop(0, j_vals[_j]))
        ax_spec.annotate(f'R({_j})', xy=(_x, _y), xytext=(_x, _y + _length), 
                         xycoords='data', textcoords='data', 
                         arrowprops=dict(color=color_r, **_arrowprop_kwargs),
                         **_arrow_kwargs)

    plt.savefig('./rot_energy_levels.pgf', bbox_inches='tight')
    plt.show()
    return ConnectionPatch, gridspec


@app.cell
def _(
    ConnectionPatch,
    Pbranch_spectrum,
    Pbranch_vals,
    Rbranch_spectrum,
    Rbranch_vals,
    e,
    gridspec,
    j_max_1,
    j_vals,
    leveldiagram_lines,
    mpl,
    np,
    plt,
    pop,
    rovibEnergy,
    wn_vals,
):
    mpl.use('pgf')
    mpl.rcParams.update({'pgf.texsystem': 'pdflatex', 'font.family': 'serif', 'font.serif': ['STIX Two Text', 'Palatino'], 'text.usetex': True, 'pgf.rcfonts': False, 'axes.titlesize': 8, 'axes.labelsize': 8, 'xtick.labelsize': 6, 'ytick.labelsize': 6})
    _fig = plt.figure(figsize=(4.318, 6))
    _plotted_js = np.arange(10)
    _xmin, _xmax = (wn_vals(298).min() - 15, wn_vals(298).max() + 45)
    _gs0 = gridspec.GridSpec(2, 1, figure=_fig, hspace=0.06, height_ratios=[4, 1])
    _gs00 = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=_gs0[0], hspace=0.03)
    ax_lvl1 = _fig.add_subplot(_gs00[0])
    ax_lvl0 = _fig.add_subplot(_gs00[1])
    _gs01 = gridspec.GridSpecFromSubplotSpec(1, 1, subplot_spec=_gs0[1])
    ax_spec = _fig.add_subplot(_gs01[0])
    for _v, ax in [(0, ax_lvl0), (1, ax_lvl1)]:
        ax.hlines(rovibEnergy(_v, _plotted_js) / e, Pbranch_vals(0, 9) - 15, Rbranch_vals(0, 8) + 15)
        ax.set_xlim(_xmin, _xmax)
    ax_lvl1.set_ylim(0.53, 0.66)
    ax_lvl0.set_ylim(0.172, 0.315)
    _d = 0.025
    _kwargs = dict(transform=ax_lvl1.transAxes, color='k', clip_on=False)
    ax_lvl1.plot((-_d, +_d), (-_d, +_d), **_kwargs)
    _kwargs.update(transform=ax_lvl0.transAxes)
    ax_lvl0.plot((-_d, +_d), (1 - _d, 1 + _d), **_kwargs)
    for ax in [ax_lvl0, ax_lvl1, ax_spec]:
        for _side in ['right', 'top']:
            ax.spines[_side].set_visible(False)
    ax_lvl1.spines['bottom'].set_visible(False)
    _xtick_params = dict(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    ax_lvl1.tick_params(**_xtick_params)
    ax_lvl0.tick_params(**_xtick_params)
    ax_lvl0.tick_params(pad=2)
    ax_lvl1.tick_params(pad=2)
    _energies = [[''], ['']]
    _levels = [[], []]
    for _v in [0, 1]:
        _levels[_v] = np.arange(j_max_1)
        for _j in leveldiagram_lines[_v][1:]:
            _energies[_v].append(f'{_j:0.3f}')
    for _v, ax in [(0, ax_lvl0), (1, ax_lvl1)]:
        ax.set_yticks(ticks=leveldiagram_lines[_v])
        ax.set_yticklabels(_energies[_v])
        ax.annotate(f'{leveldiagram_lines[_v][0]:0.3f}', xy=(wn_vals(298).min() - 27, leveldiagram_lines[_v][0]), xytext=(-19, -2), textcoords='offset points', arrowprops=dict(arrowstyle='-', fc='k', ec='k', shrinkA=0), fontsize=6, annotation_clip=False, verticalalignment='top', bbox=dict(boxstyle='square,pad=-0.1', fc='w', ec='w'))
    _jlbl_kwargs = dict(fontsize=6)
    for _v, ax, _scale in [(0, ax_lvl0, 1.015), (1, ax_lvl1, 1.005)]:
        ax.text(3095, leveldiagram_lines[_v][0] * _scale - 0.01, str(_levels[_v][0]), **_jlbl_kwargs)
        for _j in _levels[_v][1:]:
            ax.text(3095, leveldiagram_lines[_v][_j] * _scale - 0.005, str(_levels[_v][_j]), **_jlbl_kwargs)
    ax_lvl0.text(3064, leveldiagram_lines[0][9] * 1.015 - 0.005, "$J\\,''\\!=$", **_jlbl_kwargs)
    ax_lvl1.text(3066, leveldiagram_lines[1][9] * 1.005 - 0.005, "$J\\,'\\!=$", **_jlbl_kwargs)
    _trans_kwargs = dict(coordsA='data', coordsB='data', axesA=ax_lvl0, axesB=ax_lvl1, arrowstyle='-|>', linewidth=1.25)
    for _j in _levels[0][1:]:
        _x = Pbranch_vals(0, _j)
        _con = ConnectionPatch(xyA=(_x, leveldiagram_lines[0][_j]), xyB=(_x, leveldiagram_lines[1][_j - 1]), fc='b', ec='b', **_trans_kwargs)
        ax_lvl0.add_artist(_con)
    for _j in _levels[1][:-1]:
        _x = Rbranch_vals(0, _j)
        _con = ConnectionPatch(xyA=(_x, leveldiagram_lines[0][_j]), xyB=(_x, leveldiagram_lines[1][_j + 1]), fc='g', ec='g', **_trans_kwargs)
        ax_lvl0.add_artist(_con)
    ax_lvl0.text(2645, leveldiagram_lines[0][5], "$v\\,''\\!=0$", rotation='vertical', fontsize=6)
    ax_lvl1.text(2645, leveldiagram_lines[1][5], "$v\\,'\\!=1$", rotation='vertical', fontsize=6)
    _fig.text(0.05, 0.6, 'Energy (eV)', rotation='vertical', ha='center', va='center', fontsize=8)
    ax_spec.plot(wn_vals(298), np.sum([Pbranch_spectrum(0, 298), Rbranch_spectrum(0, 298)], axis=0), 'k-')
    ax_spec.set_ylim(-0.005, 0.2)
    ax_spec.set_xlim(_xmin, _xmax)
    ax_spec.set_ylabel('Absorbance')
    ax_spec.set_xlabel('Wavenumber (cm$^{-1}$)')
    ax_spec.tick_params(pad=2)
    ax_spec.yaxis.set_label_coords(-0.16, 0.5)
    _length = 0.05
    _shrink = 3
    _arrow_kwargs = dict(va='bottom', ha='center', rotation='vertical', fontsize=6, bbox=dict(boxstyle='square,pad=-0.1', fc='w', ec='w'))
    for _j in _levels[0][1:]:
        _x, _y = (Pbranch_vals(0, _j), j_vals[_j] * pop(0, j_vals[_j], 298))
        ax_spec.annotate(f'P({_j})', xy=(_x, _y), xytext=(_x, _y + _length), xycoords='data', textcoords='data', arrowprops=dict(arrowstyle='-|>', linewidth=1.25, shrinkA=_shrink, fc='b', ec='b'), **_arrow_kwargs)
    for _j in _levels[1][:-1]:
        _x, _y = (Rbranch_vals(0, _j), (j_vals[_j] + 1) * pop(0, j_vals[_j], 298))
        ax_spec.annotate(f'R({_j})', xy=(_x, _y), xytext=(_x, _y + _length), xycoords='data', textcoords='data', arrowprops=dict(arrowstyle='-|>', linewidth=1.25, shrinkA=_shrink, fc='g', ec='g'), **_arrow_kwargs)
    plt.savefig('./vibrot_energy_diagram.pgf')
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
