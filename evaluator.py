"""
Evaluating simulations with the power of multiprocessing
"""

import sympy
import numpy as np
import math
import multiprocessing
import os
from typing import List


def evaluate(
    file_prob_dist: np.ndarray,
    cache_choice_prob_dist: np.ndarray,
    num_files_cached: int,
    num_files_requested: int,
) -> np.ndarray:
    """
    Create a simulated distribution of files cached, then choose a set of files from a distribution and return results
    This is specifically for one user. Apply to meet requirements of overall simulation.

    Distribution array lengths must be the same.

    :param file_prob_dist: np.ndarray containing probability of file request
    :param cache_choice_prob_dist: np.ndarray containing probability of file caching
    :param num_files_cached: int number of files cached by user
    :param num_files_requested: int number of files requested by user
    :return: np.ndarray containing indexes chosen. Use length at discretion
    """
    assert len(file_prob_dist) == len(
        cache_choice_prob_dist
    ), "Distribution arrays must have identical index count."

    # first, choose files to be cached
    file_indexes_cached: np.ndarray = np.array([])

    # try to choose the greatest number possible
    try:
        file_indexes_cached = np.random.choice(
            len(cache_choice_prob_dist),
            num_files_cached,
            p=cache_choice_prob_dist,
            replace=False,
        )
    except ValueError as e:
        if "Fewer non-zero entries in p than size" in e.args[0]:
            number_of_nonzero_entries = np.count_nonzero(cache_choice_prob_dist)
            assert number_of_nonzero_entries < num_files_cached
            file_indexes_cached = np.random.choice(
                len(cache_choice_prob_dist),
                number_of_nonzero_entries,
                p=cache_choice_prob_dist,
                replace=False,
            )

    # next, choose files requested
    files_indexes_requested: np.ndarray = np.array([])

    # in this case, we will not permit requests asking for files in excess of lambda
    assert np.count_nonzero(file_prob_dist) >= num_files_requested

    files_indexes_requested = np.random.choice(
        len(file_prob_dist), num_files_requested, p=file_prob_dist, replace=False
    )

    # return difference
    return np.setdiff1d(files_indexes_requested, file_indexes_cached)


if __name__ == "__main__":
    print(
        evaluate(np.array([0, 0.3, 0.4, 0.3, 0]), np.array([0.2, 0.8, 0, 0, 0]), 2, 2)
    )