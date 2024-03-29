"""
Evaluating simulations with the power of multiprocessing
"""

import numpy as np
np.seterr(divide='ignore', invalid='ignore')
from typing import Any

from utils.generate_distribution_curves import (
    generate_distribution_curve,
    modify_distribution_curve,
)
from utils.parse_formula import (
    evaluate_string_to_valid_formula_str,
    parse_to_sympy,
    _unique_vars_in_formula,
)
from exceptions import InvalidParametersException


def evaluate(
    file_prob_dist: np.ndarray,
    cache_choice_prob_dist: np.ndarray,
    cache_size: int,
    num_files_requested: int,
    *args,
    **kwargs,
) -> np.ndarray:
    """
    Create a simulated distribution of files cached, then choose a set of files
    from a distribution and return results. This is specifically for one user.
    Apply to meet requirements of overall simulation.

    Distribution array lengths must be the same.

    :param file_prob_dist: np.ndarray containing probability of file request
    :param cache_choice_prob_dist: np.ndarray containing probability of file caching
    :param num_files_cached: int number of files cached by user
    :param num_files_requested: int number of files requested by user
    :param args - unused
    :param kwargs - unused
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
            cache_size,
            p=cache_choice_prob_dist,
            replace=False,
        )
    except ValueError as e:
        if "Fewer non-zero entries in p than size" in e.args[0]:
            number_of_nonzero_entries = np.count_nonzero(cache_choice_prob_dist)
            assert number_of_nonzero_entries < cache_size
            file_indexes_cached = np.random.choice(
                len(cache_choice_prob_dist),
                number_of_nonzero_entries,
                p=cache_choice_prob_dist,
                replace=False,
            )
        elif "contain NaN" in e.args[0]:
            remove_nan = np.nan_to_num(cache_choice_prob_dist)
            number_of_nonzero_entries = np.count_nonzero(remove_nan)
            file_indexes_cached = np.random.choice(
                len(cache_choice_prob_dist),
                min(number_of_nonzero_entries, cache_size),
                p=remove_nan,
                replace=False,
            )
            print(file_indexes_cached)
        else:
            raise InvalidParametersException(e.args[0])

    # next, choose files requested

    # in this case, we will not permit requests asking for files in excess of lambda
    assert np.count_nonzero(file_prob_dist) >= num_files_requested

    files_indexes_requested = np.random.choice(
        len(file_prob_dist), num_files_requested, p=file_prob_dist, replace=False
    )

    # return difference
    return np.setdiff1d(files_indexes_requested, file_indexes_cached)


def setup_and_simulate(
    formula: str,
    # file_request_distribution: np.ndarray,
    num_of_files: int,
    num_of_requests: int,
    cache_size: int,
    *args,
    **kwargs,
) -> np.ndarray:
    """
    Full, single-user simulation for a given set of arguments
    :param formula: sympy-ready formula
    :param file_request_distribution: given file distribution array
    :param num_of_requests: integer number of requests
    :param num_files_cached: integer number of files cached per user
    :param args: unused
    :param kwargs: (supply all arguments as keyword arguments in order
    to allow logic to utilize them for formula analysis)
    :return: caching results
    """

    # evaluate the formula
    formula = evaluate_string_to_valid_formula_str(formula)
    sympy_formula: Any = parse_to_sympy(formula)
    variables_to_fill = [
        var for var in _unique_vars_in_formula(formula) if var not in ["m", "r", "v"]
    ]
    var_dict = dict()

    for var in variables_to_fill:
        if var not in kwargs:
            import ipdb

            ipdb.set_trace()
        var_dict[var] = kwargs[var]

    file_request_distribution: np.ndarray = generate_distribution_curve(
                num_of_files, automatic=True, **kwargs
            )

    caching_dist = modify_distribution_curve(
        file_request_distribution, sympy_formula, **var_dict
    )

    # run evaluation
    result = evaluate(
        file_request_distribution,
        caching_dist,
        cache_size,
        num_of_requests,
        **var_dict,
    )

    return result


if __name__ == "__main__":
    print(
        evaluate(np.array([0, 0.3, 0.4, 0.3, 0]), np.array([0.2, 0.8, 0, 0, 0]), 2, 2)
    )

    argument_dict = {
        # "formula": "{p_r(m)^{1\\over\\alpha}}\\over" +
        # "{\\sum_{n=1}^{m}{p_r(n)^{1\\over\\alpha}}}}",
        "formula": "{p_r(m)^{1\\over\\alpha}}",
        "alpha": 0.9,
        "beta": 3,
        "num_files_cached": 3,
        "num_users": 2,
        "file_request_distribution": generate_distribution_curve(10, automatic=True),
        "num_of_requests": 3,
    }
    print(setup_and_simulate(**argument_dict))
