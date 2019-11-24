"""
A simple script that generates a graph without using the CacheMTR visualizer.

By Tim Bartos
"""

import matplotlib as mplcore
from matplotlib import cm
mplcore.use('tkAgg')
import matplotlib.pyplot as plt
import numpy as np
import time
from typing import *

from core.driver import Driver
from config import DEFAULT_FORMULA, POSSIBLE_SWEEPS
import config

config.USE_NUMPY_ZIPF = False

users_to_drive = 1

dr = Driver()

x_range_length = 25
y_range_length = 25
num_users = 4

dr._update_simulation_args(
    x_axis={
        "type": List[int],
        "can_be_negative": True,
        "name": "a",
    },
                            y_axis=POSSIBLE_SWEEPS["ALPHA"],
                           # y_axis=POSSIBLE_SWEEPS["CACHE_SIZE"],
                           range_x=10**np.linspace(-2, 1, x_range_length),
                            range_y=10**np.linspace(-2, 1, y_range_length),
                           # range_y=np.arange(0, y_range_length),
                            # range_y=(10**np.linspace(0, 3, y_range_length)).astype(np.int32),
                           )

dr.num_of_users = num_users
dr.number_of_files_requested = 10
dr.num_of_files = 1000

t1 = time.time()
results = dr.drive_multiple(formula=DEFAULT_FORMULA)

results = results/dr.num_of_users

print(results)
[print(str(row) + "\n") for row in results]
t2 = time.time()

num_trials = x_range_length*y_range_length*num_users
print(f"Evaluation Time: {(t2-t1):2f}seconds for {num_trials} trials, {(t2-t1)/num_trials:2f}sec/trial")

fig, (axs, ax2) = plt.subplots(1, 2, figsize=(8, 4), constrained_layout=True, dpi=200)
psm = axs.pcolormesh(dr.range_x, dr.range_y, results, cmap=cm.get_cmap('viridis', 256), rasterized=True, vmin=np.min(results), vmax=np.max(results))
colorbar = fig.colorbar(psm, ax=axs)
colorbar.ax.set_ylabel(f"Cache Misses/User")

# dist = ax2.plot(np.arange(dr.num_of_files), dr.file_dist)

title_args = [key for key in POSSIBLE_SWEEPS.keys() if key.lower() not in [dr.x_axis["name"], dr.y_axis["name"]]]
title_args.append("num_of_users")
title_args.append("num_of_files")
title = ""
for arg in title_args:
    title += f"{arg.title()}: {getattr(dr, arg.lower())}, \n"
axs.title.set_text(title)
axs.set_xscale("log")
axs.set_yscale("log")
axs.set_xlabel(dr.x_axis["name"])
axs.set_ylabel(dr.y_axis["name"])
plt.show()

