from typing import Dict

# default simulation items
DEFAULT_NUM_OF_FILES: int = 1000
DEFAULT_CACHE_SIZE: int = 10
DEFAULT_USER_NUM: int = 100
DEFAULT_REQUEST_NUM: int = 3

DEFAULT_ALPHA_START: float = 0.1
DEFAULT_ALPHA_END: float = 2.5
DEFAULT_NUMBER_OF_ALPHA: int = 10

DEFAULT_ZIPF: float = 1.0005
DEFAULT_SIMULATIONS_PER_TICK: int = 10

# other function variables
USE_NUMPY_ZIPF: bool = False
STRICT_EVALUATION: bool = False

# LaTeX config
REPLACEMENTS: Dict[str, str] = {
    "\\over": "/",
    "\\cdot": "*",
    "\\times": "*",
}
