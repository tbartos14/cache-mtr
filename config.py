from typing import Dict, Set, List, Any, Union

# default simulation items
DEFAULT_NUM_OF_FILES: int = 10
DEFAULT_CACHE_SIZE: int = 2
DEFAULT_USER_NUM: int = 3
DEFAULT_REQUEST_NUM: int = 5

DEFAULT_ALPHA: int = 3
DEFAULT_BETA: int = 5

DEFAULT_ALPHA_START: float = 0.1
DEFAULT_ALPHA_END: float = 2.5
DEFAULT_NUMBER_OF_ALPHA: int = 10

DEFAULT_ZIPF: float = 1.0005
DEFAULT_SIMULATIONS_PER_TICK: int = 10

POSSIBLE_SWEEPS: Dict[str, Dict[str, Any]] = {
    "ALPHA": {
        "type": List[Union[int, float]],
        "can_be_negative": True,
        "name": "alpha",
    },
    "BETA": {"type": List[Union[int, float]], "can_be_negative": True, "name": "beta"},
    "CACHE_SIZE": {"type": List[int], "can_be_negative": False, "name": "cache_size"},
    "NUMBER_OF_FILES_REQUESTED": {
        "type": List[int],
        "can_be_negative": False,
        "name": "num_of_requests",
    },
    "NUMBER_OF_USERS": {
        "type": List[int],
        "can_be_negative": False,
        "name": "num_users",
    },
}

DEFAULT_SWEEP_X: Dict = POSSIBLE_SWEEPS["ALPHA"]
DEFAULT_SWEEP_Y: Dict = POSSIBLE_SWEEPS["NUMBER_OF_USERS"]

DEFAULT_SWEEP_RANGE_X: DEFAULT_SWEEP_X["type"] = [
    10 ** i for i in range(-5, 6)
] if DEFAULT_SWEEP_X["can_be_negative"] else list(range(1, 11))
DEFAULT_SWEEP_RANGE_Y: DEFAULT_SWEEP_Y["type"] = list(range(-5, 6)) if DEFAULT_SWEEP_Y[
    "can_be_negative"
] else list(range(1, 11))

DEFAULT_FORMULA: str = "{{p_r(m)^{1\\over\\alpha}}\\over \\over{\\sum_{n=1}^{m}{p_r(n)^{1\\over\\alpha}}}}"

# other function variables
USE_NUMPY_ZIPF: bool = False
STRICT_EVALUATION: bool = False

# LaTeX config
REPLACEMENTS: Dict[str, str] = {
    "\\over": "/",
    "\\cdot": "*",
    "\\times": "*",
}
