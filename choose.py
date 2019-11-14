import numpy as np
import matplotlib.pyplot as plt
from typing import Optional


class numProcessManager(object):
    def __init__(self, file_zipf_scalar: float):
        self.file_distribution: Optional[np.ndarray] = None
        self.chosen_result: Optional[np.ndarray] = None
        self.file_zipf_scalar: float = file_zipf_scalar

    def create_dist(self, num_files: int, automatic: bool = False):
        if automatic:
            # generate standard zipf
            zipf: np.ndarray = np.random.zipf(self.file_zipf_scalar, num_files)

            # scale so that sum(p) = 1
            self.file_distribution = zipf.astype(np.float64)

            self.file_distribution /= self.file_distribution.sum()
            self.file_distribution.sort()
        else:
            self.file_distribution: np.ndarray = np.zeros(num_files, dtype=np.float64)

    def choose_result(self, users: int, choices: int) -> np.ndarray:
        if not isinstance(self.file_distribution, np.ndarray):
            raise Exception("Cannot choose without manager distribution")

        length = len(self.file_distribution)

        # create a resultant array with the number of choices for each user
        result_array = np.empty([users, choices], dtype=np.int32)

        for i in range(users):
            result_array[i:] = np.random.choice(
                length, choices, p=self.file_distribution, replace=True
            )

        self.chosen_result = result_array

        return result_array

    def _eval_performance(
        self, user_cache_choice: np.ndarray, chosen_results: np.ndarray,
    ):
        iterations: int = np.ma.size(chosen_results, 0)

        result_array = np.empty([iterations], dtype=np.int32)
        for i in range(iterations):
            # print(f"{chosen_results[i]} - {user_cache_choice[i]} = ", end="")
            # print(np.setdiff1d(chosen_results[i], user_cache_choice[i]))
            result_array[i:] = np.setdiff1d(
                chosen_results[i], user_cache_choice[i]
            ).size

        return result_array

    def plot(self) -> None:
        # not intended for regular use
        plt.plot(np.arange(len(self.file_distribution)), self.file_distribution)
        plt.show()


if __name__ == "__main__":
    pm = numProcessManager()
    pm.create_dist(num_files=10000, automatic=True)
    pm.plot()
