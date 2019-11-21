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


def parse_to_sympy(formula: str) -> Any:
    return parse_latex(formula)


def _unique_vars_in_formula(formula: str) -> Set[str]:
    """
    Generating sympy formulas, with some added verification that sympy
    didn't lazily parse it. Currently depreciated.

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
    unique_sympy_vars = []

    parse_latex_identified: List[Any] = list(parse_latex(formula).args)

    while len(parse_latex_identified) > 0:
        parse_latex_identified = [
            piecewise.args
            if (not isinstance(piecewise, Symbol) and not isinstance(piecewise, tuple))
            else piecewise
            for piecewise in parse_latex_identified
        ]
        # flatten
        for index, item in enumerate(parse_latex_identified):
            if isinstance(item, tuple):
                parse_latex_identified.pop(index)
                parse_latex_identified.extend(item)
            elif isinstance(item, Symbol) or item.is_Function:
                parse_latex_identified.pop(index)
                unique_sympy_vars.append(item)
            else:
                parse_latex_identified.pop(index)
                parse_latex_identified.extend(item.args)

    stringified = set([str(item) for item in unique_sympy_vars])

    # sympy seems to respect some syntax for some reason, delete remaining {}
    # stringified = {
    #     item.strip("\\").replace("{", "").replace("}", "") for item in stringified
    # }

    # assert len(stringified) == len(unique_variables)
    # assert all([var in stringified for var in unique_variables])

    return stringified


def evaluate_string_to_valid_formula_str(formula: str) -> str:
    """
    Simply cleaning up the mess
    :param formula: string containing LaTeX
    :return: string with modified variables (namely running sums and file dist func.s)
    """
    # first convert all unnecessary syntax into reasonable one-line values
    for key, value in REPLACEMENTS.items():
        formula = formula.replace(key, value)
    # clean up unnecessary spacing, it shouldn't be necessary for proper LaTeX
    formula = (
        formula.replace("\n", "").replace(" ", "").replace("\t", "").replace("\r", "")
    )

    formula = formula.replace("{\\sum_{n=1}^{m}{p_r(n)", "{v").replace("p_r(m)", "r")
    return formula


if __name__ == "__main__":
    example = (
        "{p_r(m)^{1\\over\\alpha}}\\over{\\sum_{n=1}^{m}{p_r(n)^{1\\over\\alpha}}}}"
    )
    # example = "p_r(m)^{1\\over\\alpha}"
    real_formula = evaluate_string_to_valid_formula_str(example)
    print(real_formula, parse_to_sympy(real_formula).args[1].args)
    print(
        real_formula,
        parse_to_sympy(real_formula).evalf(subs={"r": 1, "alpha": 2, "v": 2}),
    )
    print(_unique_vars_in_formula(real_formula))
