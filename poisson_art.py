#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
poisson_art.py - create city skyline art using a modified Poisson-process
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

def drawing_init(figsize=None):
    """Setup initial values for skyline art.

    :returns: Created figure for drawing.
    """
    plt.style.use("ggplot")
    fig = plt.figure(figsize=figsize) if figsize else plt.figure()

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
    return fig

def draw_picture(betas, steps, alphas, lws):
    """Draw a picture of the results from the given paramters.

    :betas: List of parameters for the pseduo-poisson processes.
    :steps: List of number of jump points to include for each process.
    :alphas: List of alpha (transparency) values for each process.
    :lws: List of line-widths for each process.
    :returns: Nothing.

    """
    results = [simulate_process(beta, steps) for beta, steps in
                    zip(betas, steps)]

    drawing_init((45, 20))
    for result, alpha, lw in zip(results, alphas, lws):
        ts, ys = result
        plt.step(ts, ys, alpha=alpha, lw=lw)

        plt.gca().set_axis_bgcolor((.95, .95, .95))
    plt.xlim(0, np.min([ts.max() for ts, ys in results]))

# Animation stuff.

betas = [1, 1, 1]
steps = [50, 50, 50]
alphas = [.3, .6, .9]
lws = [2, 3, 5]

def animations(betas, steps, alphas, lws):
    """Draw an animation of a simulation of our pseduo-poisson process.

    :betas: List of parameters for the pseduo-poisson processes.
    :steps: List of number of jump points to include for each process.
    :alphas: List of alpha (transparency) values for each process.
    :lws: List of line-widths for each process.
    :returns: Animation object.

    """
    results = [simulate_process(beta, steps) for beta, steps in
                    zip(betas, steps)]

    fig = drawing_init()
    max_t = np.min([ts.max() for ts, ys in results])
    max_y = np.max([ys.max() for ts, ys in results])
    max_y *= 1.1

    ax = plt.axes(xlim=(0, max_t), ylim=(0, max_y))
    lines = [ax.plot([0], [0], lw=lw, alpha=alpha)[0] for lw, alpha in zip(lws, alphas)]

    def init():
        for line in lines:
            line.set_data([0], [0])
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
            # There are two line segments per point.
            point_to = i // (2*frames_per_segment)

            t_start, y_start = ts[point_to], ys[point_to]
            t_end, y_end = ts[point_to + 1], ys[point_to + 1]

            plotted_ts, plotted_ys = line.get_data()
            current_t, current_y = plotted_ts[-1], plotted_ys[-1]

            # First: Move to the new t-coordinate.
            # Second: Move to the new y-coordinate.
            # This will create a bar-plot like thing.

            if not np.isclose(current_t, t_end):
                # Move to the new t-coordinate.
                dt = (t_end - t_start) / frames_per_segment
                new_t = current_t + dt
                new_y = current_y
            else:
                # Move to the new y-coordinate.
                dy = (y_end - y_start) / frames_per_segment
                new_y = current_y + dy
                new_t = current_t

            # Add new point to the list.
            new_ts = np.append(plotted_ts, new_t)
            new_ys = np.append(plotted_ys, new_y)

            line.set_data(new_ts, new_ys)

        return lines

    # TODO: Change this to "frames_per_unit" and then use segment length. This
    # will create "smoother" drawings.
    # This is difficult, because different drawings will produce different numbers
    # of frames, and matplotlib only allows a fixed number.
    frames_per_segment = 5

    n_points = len(results[0][0])
    n_segments = n_points

    # Remove the last segment so we stop trying to move after the last segment,
    # which causes an IndexError.
    # Also, times two because there are two line segments per point.
    n_frames = 2 * (frames_per_segment - 1) * n_points
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                    frames=n_frames, interval=10)

    return anim

def save_animation(anim, filename, anim_writer="ffmpeg"):
    """Save a skyline animation under the given filename.

    :anim: matplotlib.animation object.
    :filename: Filename to save animation under.
    :anim_writer: matplotlib.animation.writer option, e.g. "ffmpeg".
    :returns: Nothing.

    """
    Writer = animation.writers[anim_writer]
    writer = Writer(fps=25, metadata=dict(artist="poisson_art.py"),
                        bitrate=1800)
    anim.save(filename, writer=writer)
