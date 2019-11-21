"""
Main driver for simulation, to be used by CLI and UI
"""
from typing import List, Any, Union, Dict
import numpy as np
import multiprocessing as mp
import time

from config import *
from utils.generate_distribution_curves import generate_distribution_curve, modify_distribution_curve
from core.evaluator import evaluate, setup_and_simulate
from utils.parse_formula import evaluate_string_to_valid_formula_str, parse_to_sympy, _unique_vars_in_formula


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

        t1 = time.time()

        # evaluate the formula
        formula = evaluate_string_to_valid_formula_str(formula)
        sympy_formula: Any = parse_to_sympy(formula)
        variables_to_fill = [var for var in _unique_vars_in_formula(formula) if var not in ["m", "r", "v"]]
        var_dict = dict()

        # generate file distribution
        file_dist: np.ndarray = generate_distribution_curve(self.num_of_files, automatic=True)

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

        print(f"Time to setup: {time.time() - t1}")

        # now use multiprocessing to bring out the big guns to simulate
        caching_dists: List[List[np.ndarray]] = []
        with mp.Pool(len(self.range_x)) as p:
            for row in argument_matrix:
                async_process = [p.apply_async(setup_and_simulate, (), arg_dict) for arg_dict in row]
                caching_dists.append([result.get(timeout=10) for result in async_process])



        # add formula to kwargs
        # var_dict["formula"] = sympy_formula

        # first, generate a matrix of caching distributions beforehand
        # (assume that the file distribution will be the same for all trials,
        # this may be subject to change later)

        # print(f"Building {var_dict}")
        #
        # caching_dists: List[List[np.ndarray]] = []
        # with mp.Pool(len(self.range_y)) as p:
        #     for x in self.range_x:
        #         # modify_distribution_curve(file_dist, sympy_formula, **var_dict)
        #         async_results = [p.apply_async(modify_distribution_curve, (file_dist, sympy_formula), var_dict) for y in self.range_y]
        #         caching_dists.append([res.get(timeout=10) for res in async_results])
        #
        # # driving simulations one-by-one asynchronously (albeit poorly)
        # results: List[List[np.ndarray]] = []
        # with mp.Pool(len(self.range_y)) as p:
        #     for index_x, x in enumerate(self.range_x):
        #         # modify_distribution_curve(file_dist, sympy_formula, **var_dict)
        #         async_results = [p.apply_async(evaluate, (file_dist, caching_dists[index_x][index_y], self.cache_size, self.num_of_requests), var_dict) for index_y, y in enumerate(self.range_y)]
        #         results.append([res.get(timeout=10) for res in async_results])

        # t1 = time.time()
        # with mp.Pool(len(self.range_y)) as p:
        #     for x in self.range_x:
        #         multiple_results = [p.apply_async(add, (x, y)) for y in self.range_y]
        #         results.append([res.get(timeout=1) for res in multiple_results])
        # print(f"tdiffmp: {time.time() - t1}")
        #
        # t2 = time.time()
        # for x in self.range_x:
        #     results.append([add(x, y) for y in self.range_y])
        # print(f"tdiffmp: {time.time() - t2}")
        #
        # for prc in mp.active_children():
        #     prc.terminate()

        return [[np.array([])]]


if __name__ == "__main__":
    dr = Driver()
    print(dr.drive(formula="{p_r(m)^{1\\over\\alpha}}\\over{\\sum_{n=1}^{m}{p_r(n)^{1\\over\\alpha}}}}"))
