#!/usr/bin/env python3
"""
rot_energy_levels.py

Recreates the H35Cl rotational-vibrational energy-level diagram and
rovibrational absorption spectrum that were originally prepared in Mathematica.
"""

from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# Constants (straight copy of the notebook values)
# ----------------------------------------------------------------------
PLANCK = 6.62606896e-34        # J·s
C_LIGHT = 2.99792458e8         # m/s
K_B = 1.3806504e-23            # J/K

B = 10.59341                   # cm^-1
ALPHA = 0.30718                # cm^-1
D = 5.3194e-4                  # cm^-1
OMEGA_E = 2990.946             # cm^-1
OMEGA_E_CHI_E = 52.8186        # cm^-1

CM_TO_M = 100.0
SIGMA = 2.0                    # cm^-1 (Gaussian width used in notebook)

T_SPEC = 200.0   # K
T_LEVEL = 125.0  # used in notebook, though branch positions are temperature independent
# ----------------------------------------------------------------------
# Spectroscopic helper functions
# ----------------------------------------------------------------------
def rotational_energy(v: int, J: int) -> float:
    """Rotational energy (J) for vibrational level v and rotational quantum number J."""
    term = (B*CM_TO_M*J*(J + 1)
            - ALPHA*CM_TO_M*(v + 0.5)*J*(J + 1)
            - D*CM_TO_M*J**2*(J + 1)**2)
    return PLANCK * C_LIGHT * term


def rovibrational_energy(v: int, J: int) -> float:
    """Total rovibrational energy (J)."""
    term = (OMEGA_E*CM_TO_M*(v + 0.5)
            - OMEGA_E_CHI_E*CM_TO_M*(v + 0.5)**2
            + B*CM_TO_M*J*(J + 1)
            - ALPHA*CM_TO_M*(v + 0.5)*J*(J + 1)
            - D*CM_TO_M*J**2*(J + 1)**2)
    return PLANCK * C_LIGHT * term


def svibrot(v: int, J: int) -> float:
    """Term value (cm^-1) used for branch band positions."""
    return (OMEGA_E*(v + 0.5)
            - OMEGA_E_CHI_E*(v + 0.5)**2
            + B*J*(J + 1)
            - ALPHA*(v + 0.5)*J*(J + 1)
            - D*J**2*(J + 1)**2)


def p_branch_position(v: int, J: int) -> float:
    """Wavenumber (cm^-1) of a P-branch transition (ΔJ = -1)."""
    return svibrot(v + 1, J - 1) - svibrot(v, J)


def r_branch_position(v: int, J: int) -> float:
    """Wavenumber (cm^-1) of an R-branch transition (ΔJ = +1)."""
    return svibrot(v + 1, J + 1) - svibrot(v, J)


def q_rot(v: int, T: float) -> float:
    Js = np.arange(0, 21, dtype=float)
    energies = np.array([rotational_energy(v, int(J)) for J in Js])
    return np.sum((2 * Js + 1) * np.exp(-energies / (K_B * T)))


def population(v: int, J: int, T: float) -> float:
    numer = np.exp(-rotational_energy(v, J) / (K_B * T))
    return numer / q_rot(v, T)


def gaussian(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    return np.exp(-0.5 * ((x - mu)/sigma)**2) / (sigma * np.sqrt(2*np.pi))


def p_branch_spectrum(x: np.ndarray, v: int, T: float) -> np.ndarray:
    out = np.zeros_like(x)
    for J in range(1, 21):
        weight = J * population(v, J, T)
        out += weight * gaussian(x, p_branch_position(v, J), SIGMA)
    return out


def r_branch_spectrum(x: np.ndarray, v: int, T: float) -> np.ndarray:
    out = np.zeros_like(x)
    for J in range(0, 21):
        weight = (J + 1) * population(v, J, T)
        out += weight * gaussian(x, r_branch_position(v, J), SIGMA)
    return out


def normalization_constant(T: float) -> float:
    Js = np.arange(0, 21)
    weights = population(0, Js, T) * (2*Js + 1)
    return 1.0 / np.sum(weights)


# ----------------------------------------------------------------------
# Build spectra and level data
# ----------------------------------------------------------------------

wavenumbers = np.linspace(2670, 3070, 4000)
scale = 2 * normalization_constant(T_SPEC)
absorbance = scale * (p_branch_spectrum(wavenumbers, 0, T_SPEC) +
                      r_branch_spectrum(wavenumbers, 0, T_SPEC))

# Energy levels (in 10^-20 J for nicer numbers, matching Mathematica figure)
J_vals = np.arange(0, 10)
ground_levels = np.array([rovibrational_energy(0, J) for J in J_vals]) * 1e20
excited_levels = np.array([rovibrational_energy(1, J) for J in J_vals]) * 1e20 - 2.5

# Branch positions for callouts (J labels per notebook)
p_js = np.arange(1, 10)
r_js = np.arange(0, 9)
p_positions = np.array([p_branch_position(0, J) for J in p_js])
r_positions = np.array([r_branch_position(0, J) for J in r_js])

# Starting/ending energies for the arrows
def p_arrow_coords(J):
    return (p_branch_position(0, J),
            ground_levels[J],
            excited_levels[J-1])

def r_arrow_coords(J):
    return (r_branch_position(0, J),
            ground_levels[J],
            excited_levels[J+1])

# ----------------------------------------------------------------------
# Plotting
# ----------------------------------------------------------------------
plt.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'font.serif': ['STIX Two Text', 'Palatino'],
    'text.usetex': True,
    'pgf.rcfonts': False,
    'axes.titlesize': 8, 
    'axes.labelsize': 8,
    'xtick.labelsize': 6,
    'ytick.labelsize': 6,
})

fig = plt.figure(figsize=(4,6))
gs = fig.add_gridspec(2, 1, height_ratios=[4, 1], hspace=0.05)

ax_levels = fig.add_subplot(gs[0])
ax_spec = fig.add_subplot(gs[1], sharex=ax_levels)

# --- Energy-level diagram
for y in ground_levels:
    ax_levels.hlines(y, 2670, 3070, colors="k", linewidth=1.1)
for y in excited_levels:
    ax_levels.hlines(y, 2670, 3070, colors="k", linewidth=1.1)

ax_levels.set_xlim(2620, 3120)
ax_levels.set_ylim(2.7, 8.2)
ax_levels.set_ylabel(r"Energy")
ax_levels.set_xticks([])
ax_levels.set_yticks([])

# Custom ticks (copy of notebook choices)
ground_tick_labels = ["", "", "3.07", "3.19", "3.36", "3.57", "3.81",
                      "4.10", "4.43", "4.80"]
excited_tick_labels = ["", "", "8.80", "8.92", "9.08", "9.28",
                       "9.52", "9.80", "10.1", "10.5"]

tick_positions = list(ground_levels) + list(excited_levels)
tick_labels = ground_tick_labels + excited_tick_labels
# ax_levels.set_yticks(tick_positions, tick_labels)

# Manual labels that were placed outside the tick region in the notebook
# ax_levels.text(2587, ground_levels[0]-0.1, "2.94", va="center", fontsize=9.5)
# ax_levels.text(2587, ground_levels[1], "2.99", va="center", fontsize=9.5)
# ax_levels.text(2587, excited_levels[0]-0.1, "8.68", va="center", fontsize=9.5)
# ax_levels.text(2587, excited_levels[1], "8.72", va="center", fontsize=9.5)
# ax_levels.text(2620, 5.55, r"≈", fontsize=20, ha="center", va="center", fontfamily="STIX Two Math")

# v labels
ax_levels.text(2648, 4.0, r"$v'' = 0$", rotation=90,
               va="center", ha="center")
ax_levels.text(2648, 7.2, r"$v' = 1$", rotation=90,
               va="center", ha="center")

# J labels on the right
ax_levels.text(3075, ground_levels[-1], r"$J'' = 9$", ha="left", va="center", fontsize=9)
for J in range(8, -1, -2):
    ax_levels.text(3100, ground_levels[J], f"{J}", ha="left", va="center", fontsize=9)
ax_levels.text(3075, excited_levels[-1], r"$J' = 9$", ha="left", va="center", fontsize=9)
for J in range(8, -1, -2):
    ax_levels.text(3100, excited_levels[J], f"{J}", ha="left", va="center", fontsize=9)

# Transition arrows
color_p = (0.24, 0.35, 0.67)
color_r = (0.19, 0.5, 0.08)

for J in p_js:
    x, y0, y1 = p_arrow_coords(J)
    ax_levels.annotate("", xy=(x, y1), xytext=(x, y0),
                       arrowprops=dict(arrowstyle="-|>", color=color_p, linewidth=1.5, shrinkA=0, shrinkB=0))

for J in r_js:  
    x, y0, y1 = r_arrow_coords(J)
    ax_levels.annotate("", xy=(x, y1), xytext=(x, y0),
                       arrowprops=dict(arrowstyle="-|>", color=color_r, linewidth=1.5, shrinkA=0, shrinkB=0))

# --- Spectrum
ax_spec.plot(wavenumbers, absorbance, color="black", linewidth=1.2)
ax_spec.set_xlim(2620, 3120)
ax_spec.set_ylim(-0.01, 0.15)
ax_spec.set_xlabel(r"Wavenumber (cm$^{-1}$)")
ax_spec.set_ylabel("Absorbance")
ax_spec.set_yticks([])

# Callout arrows/labelling for P and R branches
for J in p_js:
    x = p_branch_position(0, J)
    y = scale * p_branch_spectrum(np.array([x]), 0, T_SPEC)[0]
    ax_spec.annotate(rf"$P\,({J})$", xy=(x, y), xytext=(x, y + 0.05), 
                     rotation=90, horizontalalignment='center',
                     arrowprops=dict(arrowstyle="-|>", color=color_p, linewidth=1.5))
    # ax_spec.text(x, y + 0.055, f"P({J})", color=color_p,
    #              rotation=90, ha="center", va="bottom", fontsize=11)

for J in r_js:
    x = r_branch_position(0, J)
    y = scale * r_branch_spectrum(np.array([x]), 0, T_SPEC)[0]
    ax_spec.annotate(rf"$R\,({J})$", xy=(x, y), xytext=(x, y + 0.05), 
                     rotation=90, horizontalalignment='center',
                     arrowprops=dict(arrowstyle="-|>", color=color_r, linewidth=1.5))
    # ax_spec.text(x, y + 0.055, f"R({J})", color=color_r,
    #              rotation=90, ha="center", va="bottom", fontsize=11)

plt.setp(ax_levels.get_xticklabels(), visible=False)
ax_levels.tick_params(axis="y", labelsize=9.5)
ax_spec.tick_params(axis="both", labelsize=10)

fig.savefig("rot_energy_levels.pdf", dpi=300, bbox_inches="tight")
print("Saved figure to rot_energy_levels.pgf")
