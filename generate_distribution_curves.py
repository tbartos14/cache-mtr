"""
Generating distribution curves for given sympy distribution formulas
"""

import numpy as np
import subprocess
import os
import math
import sympy
from typing import Any, List
from config import DEFAULT_ZIPF, USE_NUMPY_ZIPF, STRICT_EVALUATION


def generate_distribution_curve(
    length: int, automatic: bool = False, formula: Any = None, *args, **kwargs
) -> np.ndarray:
    """
    Generating a distribution curve
    :param length: size of array generated
    :param automatic: Whether to use an predefined, scaled Zipf distribution
    :param formula: sympa.core formula to be evaluated

    :param args: additional arguments, currently unused
    :param kwargs: passing additional arguments, including sympy formulas (use of m as a sympy symbol is illegal)
        'alpha' - kwarg specific to automatic dist
        others - supply sympy symbolic expression
    :return: np.ndarray containing distribution
    """

    if automatic:
        alpha = kwargs.get("alpha") if kwargs.get("alpha") else DEFAULT_ZIPF
        # generate standard zipf
        if USE_NUMPY_ZIPF:
            zipf: np.ndarray = np.random.zipf(alpha, length)
            zipf = zipf.astype(np.float64)

        else:
            # define zipf(m) as
            # {(1/m)^a}\over{\sum_{n=1}^{m}{({{1}\over{n}})^a}}
            if not STRICT_EVALUATION:
                with np.errstate(divide="ignore", invalid="ignore"):
                    numerator: np.ndarray = np.true_divide(
                        1, np.arange(length)
                    ) ** alpha

                    # need to remove infinite values, indicator of 0 index, evaluate as 1
                    numerator[numerator == np.inf] = 1
                    # this case won't happen for any real distribution, but who knows
                    # what i'll try later
                    numerator[numerator == -np.inf] = -1
            else:
                numerator: np.ndarray = (1 / np.arange(length)) ** alpha
            denominator: np.ndarray = np.cumsum(numerator)

            zipf: np.ndarray = numerator / denominator

        # scale so that sum(p) = 1
        zipf /= zipf.sum()
        # sort in descending order
        zipf = -np.sort(-zipf)
        return zipf
    else:
        # not the fastest implementation, but does allow for hiccups in sympy
        artificial_distribution: List[Any] = []
        for m in np.arange(length):
            symbolic_m = sympy.symbols("m")
            kwargs[symbolic_m] = m
            try:
                artificial_distribution.append(formula.evalf(subs=kwargs))
            except Exception as e:
                if STRICT_EVALUATION:
                    raise e
                else:
                    artificial_distribution.append(np.NaN)
        artificial_distribution: np.ndarray = np.array(artificial_distribution)

        # sorting is not required, use may desire unsorted distribution
        return artificial_distribution


def modify_distribution_curve(
    existing_dist: np.ndarray, formula: Any = None, *args, **kwargs
) -> np.ndarray:
    """
    Modifying distribution curves, namely for creating a caching distribution for the user
    :param existing_dist: np.ndarray distribution container
    :param formula: sympy expression mapped for each item
    :param args: currently unused
    :param kwargs: sympy expression variables (use of variable m is illegal)
    :return: np.ndarray containing the final distribution
    """
    modified_distribution: List[Any] = []
    for m in np.arange(len(existing_dist)):
        symbolic_m = sympy.symbols("m")
        kwargs[symbolic_m] = m
        try:
            modified_distribution.append(formula.evalf(subs=kwargs))
        except Exception as e:
            if STRICT_EVALUATION:
                raise e
            else:
                modified_distribution.append(np.NaN)
    modified_distribution: np.ndarray = np.array(modified_distribution)
    return modified_distribution


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    x_axis: np.ndarray = np.arange(0, 1000)

    y_axis_1 = generate_distribution_curve(1000, automatic=True, alpha=1.001)
    USE_NUMPY_ZIPF = not USE_NUMPY_ZIPF
    y_axis_2 = generate_distribution_curve(1000, automatic=True, alpha=1.001)

    plt.plot(x_axis, y_axis_1)
    plt.plot(x_axis, y_axis_2)
    plt.legend(["Original", "Numpy"])
    plt.show()
