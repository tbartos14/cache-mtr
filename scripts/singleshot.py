"""
A simple script that generates a graph without using the CacheMTR visualizer.

By Tim Bartos
"""

from core.driver import Driver
from config import DEFAULT_FORMULA

dr = Driver()
results = dr.drive(formula=DEFAULT_FORMULA)

def generate_plot(data: List, name: str, cmap):
    fig, axs = plt.subplots(1, figsize=(4, 5), constrained_layout=True, dpi=200)
    psm = axs.pcolormesh(data, cmap=cmap, rasterized=True, vmin=0, vmax=3000)
    fig.colorbar(psm, ax=axs)
    plt.savefig(name)
    plt.close()
    # plt.show()
