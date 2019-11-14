import numpy as np
from typing import List
from choose import numProcessManager
from distributions import userCacheManager
import ray
ray.init(ignore_reinit_error=True)

@ray.remote
class EvaluationDriver(object):
    def __init__(
        self,
        num_of_files: int,
        cache_size: int,
        num_of_users: int,
        num_of_requests: int,
        alpha: float,
        beta: float = 0,
        zipf_constant: float = 1.0005,
    ):
        self.num_of_files: int = num_of_files
        self.cache_size: int = cache_size
        self.num_of_users: int = num_of_users
        self.num_of_requests: int = num_of_requests
        self.alpha: float = alpha
        self.beta: float = beta

        self.trials = []

        self.pm = numProcessManager(file_zipf_scalar=zipf_constant)
        self.cm = userCacheManager()

    def drive_multiple(self, trials: int) -> None:
        for i in range(trials):
            self.drive()

    def drive(self) -> None:

        self.cm.choose_cache(self.num_of_users, self.cache_size)
        self.pm.choose_result(users=self.num_of_users, choices=self.num_of_requests)

        self.trials.append(
            sum(self.pm._eval_performance(self.cm.chosen_cache, self.pm.chosen_result))
        )

    def setup(self) -> None:
        self.pm.create_dist(num_files=self.num_of_files, automatic=True)
        self.cm.generate_distribution_curve(
            self.pm.file_distribution, self.alpha, self.beta
        )

        # currently hardcode distribution
        # self.pm.file_distribution = np.array(list(range(self.num_of_files))) / sum(
        #     range(self.num_of_files)
        # )

        self.pm.create_dist(self.num_of_files, automatic=True)

        # Also, normally we would evaluate user distribution
        assert self.pm.file_distribution.any() and self.cm.cache_p_choice.any()

    def index_files(self) -> np.ndarray:
        return np.arange(self.num_of_files)

    def _actor_return_trials(self) -> List:
        return self.trials


if __name__ == "__main__":
    d_num_of_files = 1000
    d_cache_size = 5
    d_user_num = 4
    d_request_num = 10

    eval = EvaluationDriver(
        num_of_files=d_num_of_files,
        cache_size=d_cache_size,
        num_of_users=d_user_num,
        num_of_requests=d_request_num,
        alpha=0.1,
        beta=0,
    )

    eval.setup()
    eval.drive_multiple(trials=10)

    print(f"Total transmission use: {sum(eval.trials)/len(eval.trials)}")

    # user_dist = np.zeros(num_of_files)
    #
    # for i in range(num_of_files):
    #     user_dist[i] = 1/num_of_files
    #
    # pm = numProcessManager()
    # pm.create_dist(num_files=num_of_files, automatic=True)
    # pm.file_distribution = np.array(list(range(num_of_files)))/sum(range(num_of_files))
    # pm.plot()
    #
    # cm = userCacheManager()
    # chosen_files = cm.choose_cache(user_dist, user_num, cache_size)
    # # print(f"Chosen stored indexes: {chosen_files}")
    #
    # chosen_results = pm.choose_result(users=user_num, choices=5)
    # # print(f"Chosen result indexes {chosen_results}")
    #
    # performance = pm._eval_performance(chosen_files, chosen_results)
    # print(f"Bandwidth use per user array {performance}")
    # print(f"Total transmission use: {sum(performance)}")
