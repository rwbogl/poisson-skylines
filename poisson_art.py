#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
poisson_art.py - create city skyline type things with probability
"""

import numpy as np
from itertools import accumulate
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib

def simulate_process(beta, steps):
    """
    :beta: Mean holding time.
    :steps: Number of steps to take _after_ t = 0.
    """
    holding_times = np.random.exponential(beta, steps)
    jump_times = [0] + list(accumulate(holding_times))
    states = [0] + [np.random.poisson(delta_t) for delta_t in holding_times]
    return np.array(jump_times), np.array(states)

betas = [1, 1, 1]
steps = [50, 50, 50]
alpha = [.3, .6, .9]
lws = [2, 3, 8]

def draw_picture(betas, steps, alphas, lws):
    """Draw a picture of the results from the given paramters.

    :betas: TODO
    :steps: TODO
    :alphas: TODO
    :lws: TODO
    :returns: TODO

    """
    results = [simulate_process(beta, steps) for beta, steps in
                    zip(betas, steps)]

    plt.style.use("ggplot")
    plt.figure(figsize=(18, 10))
    #plt.axis("off")
    # Turn off ticks for both axes (but don't turn off the axes, because we
    # want to do background colors).
    plt.tick_params(
        axis='both',
        which='both',
        bottom='off',
        left="off",
        labelleft="off",
        top='off',
        labelbottom='off')

    for result, alpha, lw in zip(results, alpha, lws):
        ts, ys = result
        plt.step(ts, ys, alpha=alpha, lw=lw)

        plt.gca().set_axis_bgcolor((.95, .95, .95))
    plt.xlim(0, np.min([ts.max() for ts, ys in results]))

# Animation stuff.

betas = [1, 1, 1]
steps = [50, 50, 50]
alphas = [.3, .6, .9]
lws = [2, 3, 5]

results = [simulate_process(beta, steps) for beta, steps in
                zip(betas, steps)]

fig = plt.figure(figsize=(18, 10))
max_t = np.min([ts.max() for ts, ys in results])
max_y = np.max([ys.max() for ts, ys in results])
max_y *= 1.1

ax = plt.axes(xlim=(0, max_t), ylim=(0, max_y))
lines = [ax.step([], [], lw=lw, alpha=alpha)[0] for lw, alpha in zip(lws, alphas)]

plt.tick_params(
    axis='both',
    which='both',
    bottom='off',
    left="off",
    labelleft="off",
    top='off',
    labelbottom='off')

def init():
    for line in lines:
        line.set_data([], [])
    return lines

def animate(i):
    global results
    if i == 0:
        # Create new results to plot.
        results = [simulate_process(beta, steps) for beta, steps in
                        zip(betas, steps)]
        max_t = np.min([ts.max() for ts, ys in results])
        max_y = np.max([ys.max() for ts, ys in results])
        max_y *= 1.1
        plt.xlim(0, max_t)
        plt.ylim(0, max_y)

    for result, line in zip(results, lines):
        ts, ys = result
        ts, ys = ts[:i], ys[:i]
        line.set_data(ts, ys)

    return lines

plt.style.use("ggplot")
anim = animation.FuncAnimation(fig, animate, init_func=init,
                                frames=len(results[0][0]), interval=60)
plt.show()
