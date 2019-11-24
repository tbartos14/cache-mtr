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
    POSSIBLE_SWEEPS
)
from exceptions import InvalidParametersException

from utils.generate_distribution_curves import generate_distribution_curve
from core.evaluator import setup_and_simulate
from utils.parse_formula import evaluate_string_to_valid_formula_str


class Driver(object):
    def __init__(self, *args, **kwargs) -> None:
        self._reset_args()

    def _reset_args(self) -> None:
        self.file_dist: np.ndarray = np.array([])
        self.x_axis = DEFAULT_SWEEP_X
        self.y_axis = DEFAULT_SWEEP_Y
        self.range_x = DEFAULT_SWEEP_RANGE_X
        self.range_y = DEFAULT_SWEEP_RANGE_Y
        self.num_of_files = DEFAULT_NUM_OF_FILES
        self.cache_size = DEFAULT_CACHE_SIZE
        self.number_of_files_requested = DEFAULT_REQUEST_NUM
        self.num_of_users = DEFAULT_USER_NUM
        self.alpha = DEFAULT_ALPHA
        self.beta = DEFAULT_BETA

        self.file_distribution: np.ndarray = np.array([])

    def _update_distribution(self, *args, **kwargs) -> None:
        self.file_distribution = generate_distribution_curve(*args, **kwargs)

    def _update_simulation_args(
        self,
        x_axis: Dict[str, Any],
        y_axis: Dict[str, Any],
        range_x: Union[List[Union[int, float]], np.ndarray],
        range_y: Union[List[Union[int, float]], np.ndarray],
    ):
        # assert x_axis["name"].upper() in POSSIBLE_SWEEPS
        self.x_axis = x_axis
        self.range_x = range_x
        # assert y_axis["name"].upper() in POSSIBLE_SWEEPS
        self.y_axis = y_axis
        self.range_y = range_y


    def drive_multiple(self, formula: str) -> np.ndarray:
        """
        Driving multiple simulations.
        :param formula: formula string provided
        :param num_users: number of users (the number of the independent
         user simulations to perform
        :return: x,y matrix of TOTAL caching misses
        """

        # generate file distribution
        self.file_dist: np.ndarray = generate_distribution_curve(
            self.num_of_files, automatic=True
        )

        trials: List[np.ndarray] = []
        for i in range(self.num_of_users):
            trials.append(self.drive(formula=formula, generate_new_dist=False))

            bars_left_to_complete = int(20*i/self.num_of_users)
            print(f":{bars_left_to_complete * '#'}{(20 - bars_left_to_complete) * '-'}: {(100 * i/self.num_of_users):.2f}%")

        return sum(trials)

    def drive(self, formula: str, generate_new_dist: bool = False) -> np.ndarray:
        """
        Driving simulations.
        :param: formula: formula string provided
        :return: x,y matrix of caching misses
        """

        # evaluate the formula
        formula = evaluate_string_to_valid_formula_str(formula)

        if generate_new_dist:
            # generate file distribution
            self.file_dist: np.ndarray = generate_distribution_curve(
                self.num_of_files, automatic=True,
            )

        # pre-populate a matrix of arguments
        default_arguments: Dict[str, Any] = {
            "formula": formula,
            "alpha": self.alpha,
            "beta": self.beta,
            "cache_size": self.cache_size,
            "num_users": self.num_of_users,
            # "file_request_distribution": self.file_dist,
            "num_of_requests": self.number_of_files_requested,
            "num_of_files": self.num_of_files,
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

        # for now, return the length of caching purposes
        # if needed, exact indexes are still available for index

        for index, row in enumerate(caching_dists):
            caching_dists[index] = [len(item) for item in row]

        return np.array(caching_dists)


if __name__ == "__main__":
    dr = Driver()
    print(
        dr.drive(
            formula="{p_r(m)^{1\\over\\alpha}}\\over"
            + "{\\sum_{n=1}^{m}{p_r(n)^{1\\over\\alpha}}}}"
        )
    )
