"""
Related utilities for printing/verifying latex inputs
"""
import requests
import urllib.parse


def get_latex_png(formula: str) -> None:
    """
    Uses QuickLaTeX API to create IMG of written formula
    :param formula: string containing LaTeX formula
    :return: Error code [0,1] (saves to img.png locally)
    """

    formula = formula.replace(" ", "")
    arguments = {
        "formula": "\\begin{align*}\n{" + formula + "}\n\\end{align*}",
        "fsize": "17px",
        "fcolor": "000000",
        "mode": "0",
        "out": "1",
        "remhost": "quicklatex.com",
        "preamble": "\\usepackage{amsmath}\n\\usepackage{amsfonts}\n\\usepackage{amssymb}",
        "rnd": "82.19820292929282",
    }

    response = requests.post("https://quicklatex.com/latex3.f", data=arguments)
    if response.status_code != 200:
        return 1

    url = response.text.replace("\n", " ").split(" ")[1].strip()
    if url == "https://quicklatex.com/cache3/error.png":
        return 1
    response = requests.get(url)
    # response.raw.decoded_content = True
    with open("img.png", "wb") as out_file:
        out_file.write(response.content)
    del response
    return 0


if __name__ == "__main__":
    print(get_latex_png("x^2"))
