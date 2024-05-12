import pandas as pd
from pandas import Series
import numpy as np

rs_state = {
    "01": "Schleswig-Holstein",
    "02": "Hamburg",
    "03": "Niedersachsen",
    "04": "Bremen",
    "05": "Nordrhein-Westfalen",
    "06": "Hessen",
    "07": "Rheinland-Pfalz",
    "08": "Baden-Württemberg",
    "09": "Bayern",
    "10": "Saarland",
    "11": "Berlin",
    "12": "Brandenburg",
    "13": "Mecklenburg-Vorpommern",
    "14": "Sachsen",
    "15": "Sachsen-Anhalt",
    "16": "Thüringen"
}
state_rs = {v: k for k, v in rs_state.items()}


def num(number: float, separator: str = ".", magnitude: str = None, digits: int = 0, lang: str = "de", space: str = "&#x202F;"):
    """
    Display numbers in a friendly way.

    :param number: any float or integer
    :param magnitude: say if you want thousands (k), millions (M) or billions (G) - or none
    :param digits: how many digits after the decimal should be displayed (after division by magnitude)
    :param lang: German (de) or English (en). Defaults to German.
    :param space: character(s) between the number and magnitude string, if any. Defaults to "narrow non-breaking space".
    """
    magwords = {
        "k": {
            "div": 1000,
            "de": " Tsd.",
            "en": "k",
        },
        "M": {
            "div": 1e6,
            "de": " Mio.",
            "en": "m",
        },
        "G": {
            "div": 1e9,
            "de": " Mrd.",
            "en": "bn",
        },
        None: {
            "div": 1,
            "de": "",
            "en": "",
        }
    }

    # throw out nans
    if pd.isna(number):
        return ""

    if magnitude == "auto":
        if int(number) < 1e6:
            magnitude = None
        elif int(number) < 1e9:
            magnitude = "M"
        else:
            magnitude = "G"

    number = number / magwords[magnitude]["div"] if magnitude in magwords.keys() else number
    number = round(number, digits) if digits is not None else number

    if type(number) == Series:
        number = number.iloc[0]


    # remove ,0 if so desired:
    if digits == 0 or number == int(number):
        number = int(number)

    # add thousand separator if so desired:
    if separator != "":
        numstring = "{:,}".format(number)

        if lang == "de":
            inter1 = numstring.replace(",", "§")  # thousand sep to placeholder
            inter2 = inter1.replace(".", ",")  # point to German comma
            numstring = inter2.replace("§", separator)  # placeholder to sep

    else:
        numstring = str(number)
        if lang == "de":
            numstring = numstring.replace(".", ",")

    suffix = magwords[magnitude][lang] if magnitude is not None else ""

    outstring = numstring + space + suffix

    return outstring


def ticker(x):
    """
    Automatic tick finding, so we can apply text functions before plotting ticks.
    This fills in on a missing plotly feature: we want prettified locale-correct
    tick labels that are found automatically.
    """

    def rounder(number):
        """
        Round a number to one nonzero digit and return the result along with the order of magnitude.
        """
        if number == 0:
            return 0, 0

        # Calculate the order of magnitude
        order_magnitude = 1 / (10 ** int(-np.floor(np.log10(abs(number)))))

        # Round the number to one nonzero digit
        rounded_number = round(number / order_magnitude) * order_magnitude

        return rounded_number, order_magnitude

    rounded, mag = rounder(x)
    seq = np.arange(0, rounded + 1, mag)

    if len(seq) > 8:
        seq = seq[::2]

    else:
        multiplier = 2
        while len(seq) < 5:
            seq = np.arange(0, x*multiplier + 1, mag) / multiplier
            multiplier *= 2

    return [round(i) for i in seq]


def cuyo(fig, s: str):
    """
    Return the index of the trace in <fig> whose name contains <s>.
    """
    matches = []
    names = [i.name for i in fig.data]

    for i, entry in enumerate(names):
        if s in entry:
            matches.append(i)
    
    return matches
