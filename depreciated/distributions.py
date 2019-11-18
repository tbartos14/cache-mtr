import subprocess
import os
import math
import numpy as np

# from .lt.latex2sympy.process_latex import process_sympy
# import sympy
# from sympy.abc import alpha, beta


class userCacheManager(object):
    def __init__(self):
        self.chosen_cache: np.ndarray = np.array([])
        self.expression: str = ""
        self.cache_p_choice: np.ndarray = np.array([])

    def generate_distribution_curve(
        self, file_distribution: np.ndarray, alpha: float, beta: float = 0,
    ):
        # use shorthand
        p_r = file_distribution

        # generate distribution from given formula

        # special case
        if alpha == 0:
            p_r_m_power = np.zeros_like(p_r)
            p_r_m_power[-1] = 1
        else:
            p_r_m_power = np.power(p_r, 1 / alpha)
        self.cache_p_choice = p_r_m_power / sum(p_r_m_power)

    def choose_cache(self, user_num: int, cache_size: int) -> np.ndarray:
        assert isinstance(self.cache_p_choice, np.ndarray)

        length = len(self.cache_p_choice)

        result_array = np.empty([user_num, cache_size], dtype=np.int32)

        for i in range(user_num):
            # try to choose the greatest number possible
            try:
                result_array[i:] = np.random.choice(
                    length, cache_size, p=self.cache_p_choice, replace=False
                )
            except ValueError as e:
                if "Fewer non-zero entries in p than size" in e.args[0]:
                    number_of_nonzero_entries = np.count_nonzero(self.cache_p_choice)
                    assert number_of_nonzero_entries < cache_size
                    result_array[i:] = np.random.choice(
                        length,
                        number_of_nonzero_entries,
                        p=self.cache_p_choice,
                        replace=False,
                    )

        self.chosen_cache = result_array

        return result_array

    def _interpret_expression(self, expression: str):
        # hardcode the replacement for certain latex issues
        expression = expression.lower().strip()
        expression.replace("\sum{p_r(m)}", "s")

        # define variables to make up external
        #
        expression = process_sympy(expression)

    def add_expression(self, expression: str):
        self.expression = expression
        try:
            self._interpret_expression(expression)
            return 1
        except:
            return 0


if __name__ == "__main__":
    cm = userCacheManager()
    file_dist = np.zeros(10000)

    for i in range(10000):
        file_dist[i] = 1 / 10000

    cm.generate_distribution_curve(file_dist, alpha=0.1)
    print(cm.choose_cache(5, 4))
