import multiprocessing
from main import EvaluationDriver
from config import (
    DEFAULT_CACHE_SIZE,
    DEFAULT_NUM_OF_FILES,
    DEFAULT_REQUEST_NUM,
    DEFAULT_USER_NUM,
    DEFAULT_ALPHA_END,
    DEFAULT_ALPHA_START,
    DEFAULT_NUMBER_OF_ALPHA,
    DEFAULT_ZIPF,
    DEFAULT_SIMULATIONS_PER_TICK,
)

alphas = range(1, 11)
cache_size = range(1, 11)

# because multiprocessing is so stupid it can't fathom the idea of a lambda
def setup(x):
    return x.setup()


def drive_multiple(x):
    return x.setup()


def return_trials(x):
    return x._actor_return_trials()


# time it!
for alpha in alphas:
    with multiprocessing.Pool(len(cache_size)) as p:
        obj_actors = [
            EvaluationDriver(
                num_of_files=DEFAULT_NUM_OF_FILES,
                cache_size=cache,
                num_of_users=DEFAULT_USER_NUM,
                num_of_requests=DEFAULT_REQUEST_NUM,
                alpha=alpha,
                zipf_constant=DEFAULT_ZIPF,
            )
            for cache in cache_size
        ]
        print(obj_actors[0].__dict__)
        p.map(setup, obj_actors)
        p.map(drive_multiple, obj_actors)
        print(p.map(return_trials, obj_actors))

for prc in multiprocessing.active_children():
    prc.terminate()
