#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

npts = 500
xdata = np.linspace(-5,5,npts)

def lineshape(nu, nuA, nuB, tau):
    numerator = tau * (nuA - nuB)**2
    denominator = (0.5 * (nuA + nuB) - nu)**2 + \
        (2 * np.pi * tau * (nuA - nu) * (nuB - nu))**2
    return numerator / denominator
    

ydata = lineshape(xdata, -2, 2, 0.5)

def find_intersections(x, y, C):
    # Contains numpy indexing tricks that can be hard to reproduce
    # in the case where both functions are non-constants
    ii, = np.nonzero((y[1:]-C)*(y[:-1]-C) < 0.)  # intersection indices
    x_intersections = x[ii] + (C - y[ii])/(y[1+ii] - y[ii])*(x[1+ii] - x[ii])
    y_intersections = C * np.ones(len(ii))
    return x_intersections, y_intersections


# Intersection point (half height)
C = 0.5 * np.max(ydata)

xint, yint = find_intersections(xdata, ydata, C)

plt.figure()
plt.plot(xdata, ydata)
plt.plot(xint, yint, 'ro')
plt.show()

specdata = np.c_[xdata,ydata]
intdata = np.c_[xint,yint]
np.savetxt("src/figures/slow_spec.csv", specdata, fmt="%5f", delimiter='\t')
np.savetxt("src/figures/slow_int.csv", intdata, fmt="%5f", delimiter='\t')