"""
Main driver for simulation, to be used by CLI and UI
"""
import numpy as np
import multiprocessing as mp
from typing import List, Union, Dict, Any

from config import (
    DEFAULT_SWEEP_RANGE_X,
    DEFAULT_SWEEP_RANGE_Y,
    DEFAULT_SWEEP_X,
    DEFAULT_SWEEP_Y,
    DEFAULT_NUM_OF_FILES,
    DEFAULT_CACHE_SIZE,
    DEFAULT_USER_NUM,
    DEFAULT_REQUEST_NUM,
    DEFAULT_ALPHA,
    DEFAULT_BETA,
)
from exceptions import InvalidParametersException

from utils.generate_distribution_curves import generate_distribution_curve
from core.evaluator import setup_and_simulate
from utils.parse_formula import evaluate_string_to_valid_formula_str


class Driver(object):
    def __init__(self, *args, **kwargs) -> None:
        self.data: List[List[int]] = []
        self.x_axis = DEFAULT_SWEEP_X
        self.y_axis = DEFAULT_SWEEP_Y
        self.range_x = DEFAULT_SWEEP_RANGE_X
        self.range_y = DEFAULT_SWEEP_RANGE_Y
        self.num_of_files = DEFAULT_NUM_OF_FILES
        self.cache_size = DEFAULT_CACHE_SIZE
        self.num_of_requests = DEFAULT_REQUEST_NUM
        self.num_of_users = DEFAULT_USER_NUM
        self.alpha = DEFAULT_ALPHA
        self.beta = DEFAULT_BETA

        self.file_distribution: np.ndarray = np.array([])

    def _update_distribution(self, *args, **kwargs) -> None:
        self.file_distribution = generate_distribution_curve(*args, **kwargs)

    def _update_simulation_args(
        self,
        x_axis: str,
        y_axis: str,
        range_x: List[Union[int, float]],
        range_y: List[Union[int, float]],
    ):
        pass

    def drive(self, formula: str) -> List[List[np.ndarray]]:
        """
        Driving simulations.
        :param: formula: formula string provided
        :return: x,y matrix of caching misses
        """

        # evaluate the formula
        formula = evaluate_string_to_valid_formula_str(formula)

        # generate file distribution
        file_dist: np.ndarray = generate_distribution_curve(
            self.num_of_files, automatic=True
        )

        # pre-populate a matrix of arguments
        default_arguments: Dict[str, Any] = {
            "formula": formula,
            "alpha": self.alpha,
            "beta": self.beta,
            "num_files_cached": self.cache_size,
            "num_users": self.num_of_users,
            "file_request_distribution": file_dist,
            "num_of_requests": self.num_of_requests,
        }
        argument_matrix: List[List[Dict[str, Any]]] = []
        for _ in self.range_y:
            # shallow copy the arguments
            argument_matrix.append([default_arguments.copy() for _ in self.range_x])

        # then, sweep for each range
        for index_y, value_y in enumerate(self.range_y):
            for index_x, value_x in enumerate(self.range_x):
                argument_matrix[index_y][index_x][self.x_axis["name"]] = value_x
                argument_matrix[index_y][index_x][self.y_axis["name"]] = value_y

        # now use multiprocessing to bring out the big guns to simulate
        caching_dists: List[List[np.ndarray]] = []
        try:
            with mp.Pool(len(self.range_x)) as p:
                for row in argument_matrix:
                    async_process = [
                        p.apply_async(setup_and_simulate, (), arg_dict)
                        for arg_dict in row
                    ]
                    caching_dists.append(
                        [result.get(timeout=10) for result in async_process]
                    )
        except Exception as e:
            if "division by zero" in e.args[0].lower():
                raise InvalidParametersException(
                    "Attempted to divide in range containing 0"
                )

        for prc in mp.active_children():
            prc.terminate()

        return caching_dists


if __name__ == "__main__":
    dr = Driver()
    print(
        dr.drive(
            formula="{p_r(m)^{1\\over\\alpha}}\\over"
            + "{\\sum_{n=1}^{m}{p_r(n)^{1\\over\\alpha}}}}"
        )
    )
