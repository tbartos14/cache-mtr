import ray
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

ray.init(ignore_reinit_error=True)

alphas = range(1, 11)
cache_size = range(1, 11)

# time it!
for alpha in alphas:
    obj_actors = [
        EvaluationDriver.remote(
            num_of_files=DEFAULT_NUM_OF_FILES,
            cache_size=cache,
            num_of_users=DEFAULT_USER_NUM,
            num_of_requests=DEFAULT_REQUEST_NUM,
            alpha=alpha,
            zipf_constant=DEFAULT_ZIPF,
        )
        for cache in cache_size
    ]
    [actor.setup.remote() for actor in obj_actors]
    [actor.drive_multiple.remote(100) for actor in obj_actors]
    print(ray.get([actor._actor_return_trials.remote() for actor in obj_actors]))

# this method seems to produce enormous amounts of headless threads afterwards, destroying
# my activity manager
