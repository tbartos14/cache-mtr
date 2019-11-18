"""
Fairly complex system of parsing formulas, necessary to make formulas useful

Sympy is capable of interpreting LaTeX, but it does so quite awfully, ignoring
just about everything important that can be evaluated, like sums and functions.
This module permits the use of sympy expressions by adding decorated functions as
replacements for normally-omitted variables.

"""
from typing import Any, Set, List
import sympy
from sympy.core.symbol import Symbol
from sympy.parsing.latex import parse_latex

from config import REPLACEMENTS


def unique_vars_in_formula(formula: str) -> Set[str]:
    """
    Generating sympy formulas, with some added verification that sympy
    didn't lazily parse it

    :param formula: LaTeX string
    :return: set of unique variables required in formula, neglected by sympy sometimes
    """

    # first convert all unnecessary syntax into reasonable one-line values
    for key, value in REPLACEMENTS.items():
        formula = formula.replace(key, value)
    # clean up unnecessary spacing, it shouldn't be necessary for proper LaTeX
    formula = (
        formula.replace("\n", "").replace(" ", "").replace("\t", "").replace("\r", "")
    )

    # separate on legitimate latex mathematics
    variables: List[str] = [formula]
    for op in ["+", "-", "*", "/", "^"]:
        variables = list(
            map(lambda x: x.strip().strip("{").strip("}").split(op), variables)
        )
        variables = [item for sublist in variables for item in sublist]

    # there may be some legitimate semantics left, namely implicit multiplication
    # with parentheses, but taking note of defined functions
    for index, var in enumerate(variables):
        # assume all defined functions contain "_"
        if ("(" in var or ")" in var) and "_" not in var and "\\" not in var:
            split_vars = [item.split("(") for item in var.split(")")]
            split_vars = [item for sublist in split_vars for item in sublist]
            variables.pop(index)
            variables.extend(split_vars)

    # separate any remaining garlic items
    for index, var in enumerate(variables):
        if len(var) > 1 and "_" not in var and "\\" not in var:
            split_vars = [char for char in var if char not in ",.0123456789"]
            variables.pop(index)
            variables.extend(split_vars)

    # last, disregard numericals and empty strings and require unique
    unique_variables: Set[str] = set(
        [char for char in variables if char not in ",.0123456789"]
    )

    parse_latex_identified: List[Any] = list(parse_latex(formula).args)
    print(f"parse_latex_identified {parse_latex_identified}")
    while any(map(lambda x: not isinstance(x, Symbol), parse_latex_identified)):
        parse_latex_identified = [
            piecewise.args if (not isinstance(piecewise, Symbol)) else piecewise
            for piecewise in parse_latex_identified
        ]
        # flatten
        for index, item in enumerate(parse_latex_identified):
            if isinstance(item, tuple):
                parse_latex_identified.pop(index)
                parse_latex_identified.extend(item)

    stringified = set([str(item) for item in parse_latex_identified])
    print(f"Final result: {stringified}")

    assert len(stringified) == len(unique_variables)
    assert all([var in stringified for var in unique_variables])

    return unique_variables


str_latex = r"x*y*\sump_r(m)"

if __name__ == "__main__":
    example = "{(2.0zxy)x*2*\sump_r(m)}\over{\\beta^2}"
    # example = "2x*x*y"
    print(unique_vars_in_formula(example))
