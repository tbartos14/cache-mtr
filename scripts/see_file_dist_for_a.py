from matplotlib import pyplot as plt
import numpy as np

import config

config.USE_NUMPY_ZIPF = False
num_of_files = config.DEFAULT_NUM_OF_FILES
a = 1.05

from utils.generate_distribution_curves import generate_distribution_curve

file_dist: np.ndarray = generate_distribution_curve(
    num_of_files, automatic=True, **{"a": a}
)

plt.plot(np.arange(num_of_files), file_dist)
plt.title(f"File Distribution for Zipf a={a}")
plt.xlabel(f"Index (m)")
plt.ylabel(f"Probability of Caching (p_c)")
plt.show()

