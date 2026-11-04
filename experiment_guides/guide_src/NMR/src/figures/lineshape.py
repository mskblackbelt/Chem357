#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "matplotlib>=3.10.9",
#     "numpy>=2.4.6",
# ]
# ///

# Writes the *_spec.csv and *_int.csv data for lineshapes.tex.
# Pass --plot to preview each lineshape.

import sys
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
dname = Path(__file__).parent.resolve()


npts = 500
xdata = np.linspace(-5,5,npts)

def lineshape(nu, nuA, nuB, tau):
    numerator = tau * (nuA - nuB)**2
    denominator = (0.5 * (nuA + nuB) - nu)**2 + \
        (2 * np.pi * tau * (nuA - nu) * (nuB - nu))**2
    return numerator / denominator

def find_intersections(x, y, C):
    # Contains numpy indexing tricks that can be hard to reproduce
    # in the case where both functions are non-constants
    ii, = np.nonzero((y[1:]-C)*(y[:-1]-C) < 0.)  # intersection indices
    x_intersections = x[ii] + (C - y[ii])/(y[1+ii] - y[ii])*(x[1+ii] - x[ii])
    y_intersections = C * np.ones(len(ii))
    return x_intersections, y_intersections


taus = [0.5, 0.12, 0.056, 0.005]
prefixes = ["slow", "interm", "coalesc", "fast"]    
params = zip(taus, prefixes)

for tau, name in params:
    ydata = lineshape(xdata, -2, 2, tau)
    ydata = ydata / ydata.max()

    # Intersection point (half height)
    C = 0.5 * np.max(ydata)

    xint, yint = find_intersections(xdata, ydata, C)

    if "--plot" in sys.argv:
        plt.figure()
        plt.plot(xdata, ydata)
        plt.plot(xint, yint, 'ro')
        plt.title(name.capitalize())
        plt.show()

    specdata = np.c_[xdata,ydata]
    intdata = np.c_[xint,yint]
    spec_file = name + "_spec.csv"
    int_file = name + "_int.csv"    
    np.savetxt(dname / spec_file, specdata, fmt="%5f", delimiter='\t')
    np.savetxt(dname / int_file, intdata, fmt="%5f", delimiter='\t')