"""
A simple script that generates a graph without using the CacheMTR visualizer.

By Tim Bartos
"""

import matplotlib as mplcore
from matplotlib import cm
mplcore.use('tkAgg')
import matplotlib.pyplot as plt
import numpy as np

from core.driver import Driver
from config import DEFAULT_FORMULA, POSSIBLE_SWEEPS

users_to_drive = 1

dr = Driver()
dr._update_simulation_args(x_axis=POSSIBLE_SWEEPS["ALPHA"],
                           y_axis=POSSIBLE_SWEEPS["CACHE_SIZE"],
                           range_x=10**np.linspace(-1, 1, 25),
                           range_y=np.arange(0, 25))

dr.num_of_users = 1
dr.number_of_files_requested = 3
dr.num_of_files = 1000

results = dr.drive_multiple(formula=DEFAULT_FORMULA)
results = results/dr.num_of_users

fig, axs = plt.subplots(1, figsize=(4, 5), constrained_layout=True, dpi=200)
psm = axs.pcolormesh(dr.range_x, dr.range_y, results, cmap=cm.get_cmap('viridis', 256), rasterized=True, vmin=np.min(results), vmax=np.max(results))
colorbar = fig.colorbar(psm, ax=axs)
colorbar.ax.set_ylabel(f"Cache Misses/User")

title_args = [key for key in POSSIBLE_SWEEPS.keys() if key.lower() not in [dr.x_axis["name"], dr.y_axis["name"]]]
title_args.append("num_of_users")
title = ""
for arg in title_args:
    title += f"{arg.title()}: {getattr(dr, arg.lower())}, \n"
axs.title.set_text(title)
axs.set_xscale("log")
axs.set_xlabel(dr.x_axis["name"])
axs.set_ylabel(dr.y_axis["name"])
plt.show()

