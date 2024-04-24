import re

import pandas as pd


geburten = "data/raw/destatis 12612-0100 - Geburten 2009-2021.csv"
eg_empf  = "data/raw/destatis 22922-0025 - Elterngeldempfänger 2009-2021.csv"
eg_hoehe = "data/raw/destatis 22922-0118 - dschn Höhe Elterngeld.csv"
eg_dauer = "data/raw/destatis 22922-0125 - dschn Dauer EGeld Kreise.csv"
steuer   = "data/raw/regionalstatistik 73111-01-01-4 - Steuern.csv"
ewz      = "data/raw/destatis 12411-0010 - Bevölkerung.csv"

#
# Geburten
# 
df = pd.read_csv(
    geburten,
    encoding="latin-1",
    sep=";",
    skiprows=4,
    skipfooter=3,
    engine="python",
)
df = (df
 .rename({"Unnamed: 0": "land", "Unnamed: 1": "fm"}, axis=1)
 .set_index(["land", "fm"])
 .loc[(slice(None), ["männlich", "weiblich"]), :]
 .rename_axis(axis=1, mapper="jahr")
 .stack()
 .to_frame("geburten")
 .reorder_levels(["jahr", "land", "fm"])
 .sort_index()
 .reset_index()
 .astype({"jahr": pd.Int64Dtype()})
)

df.to_parquet("data/processed/geburten.parquet")


#
# Empfangende von Elterngeld
#
df = pd.read_csv(
    eg_empf,
    encoding="latin-1",
    sep=";",
    skiprows=6,
    header=[0, 1],
    skipfooter=25,
    engine="python",
)

df = (df
    .rename(columns={"Unnamed: 0_level_0": "land",
                     "Unnamed: 1_level_0": "fm",
                     "Unnamed: 2_level_0": "art",
                     "Unnamed: 0_level_1": "",
                     "Unnamed: 1_level_1": "",
                     "Unnamed: 2_level_1": ""})
    .rename_axis(columns=("jahr", "quartal"))
)

df.columns = ['_'.join(col).strip() for col in df.columns.values]

df = (
    df
    .drop("2021_4. Quartal", axis=1)
    .rename(columns={"land_": "land", "fm_": "fm", "art_": "art"})
    .set_index(["land", "fm", "art"])
    .rename_axis("jahr_quartal", axis=1)
    .stack()
    .to_frame("pers")
    .reset_index(level=3)
    .assign(jahr=lambda x: x["jahr_quartal"].str.extract(r"(\d{4})"))
    .assign(quartal=lambda x: x["jahr_quartal"].str[5])
    .drop("jahr_quartal", axis=1)
    .set_index(["jahr", "quartal"], append=True)
    .reorder_levels(["jahr", "quartal", "land", "fm", "art"])
    .reset_index()
    .astype({"jahr": pd.Int64Dtype(), "quartal": pd.Int64Dtype()})
)

df.to_parquet("data/processed/eg_empf.parquet")


#
# Höhe des Elterngeldes
#
df = pd.read_csv(
    eg_hoehe,
    encoding="latin-1",
    sep=";",
    skiprows=6,
    header=[0, 1],
    skipfooter=3,
    engine="python",
)

df = (df
      .rename(columns={"Unnamed: 0_level_0": "state",
                     "Unnamed: 1_level_0": "sex",
                     "Unnamed: 2_level_0": "egplus",
                     "Unnamed: 3_level_0": "erwerbstaetig",
                     "Unnamed: 0_level_1": "",
                     "Unnamed: 1_level_1": "",
                     "Unnamed: 2_level_1": "",
                     "Unnamed: 3_level_1": "",})
      .rename_axis(columns=("year", "quarter"))
)

df.columns = ['_'.join(col).strip() for col in df.columns.values]

df = (
    df
    .rename(columns={"state_": "state", "sex_": "sex", "egplus_": "egplus", "erwerbstaetig_": "erwerbstaetig"})
    .set_index(["state", "sex", "egplus", "erwerbstaetig"])
    .rename_axis("year_quarter", axis=1)
    .stack()
    .to_frame("eur")
    .reset_index(level=4)
    .assign(year=lambda x: x["year_quarter"].str.extract(r"(\d{4})"))
    .assign(quarter=lambda x: x["year_quarter"].str[5])
    .drop("year_quarter", axis=1)
    .set_index(["year", "quarter"], append=True)
    .reorder_levels(["year", "quarter", "state", "egplus", "erwerbstaetig", "sex"])
    .sort_index()
    .reset_index()
)

df = df.astype({
    "state": pd.StringDtype(),
    "year": pd.Int64Dtype(),
    "quarter": pd.Int64Dtype(),
    "egplus": pd.StringDtype(),
    "erwerbstaetig": pd.StringDtype(),
    "sex": pd.StringDtype(),
    "eur": pd.Int64Dtype(),
})

df.to_parquet("data/processed/eg_hoehe.parquet")


#
# Dauer des Elterngeldes
#
df = pd.read_csv(
    eg_dauer,
    encoding="latin-1",
    sep=";",
    skiprows=5,
    skipfooter=4,
    engine="python",
)

df = (df
      .rename(columns={"Unnamed: 0": "krs",
                       "Unnamed: 1": "fm",
                       "Unnamed: 2": "egplus",})
      .rename_axis(columns="jahr")
)

df = (
    df
    .set_index(["krs", "fm", "egplus"])
    .stack()
    .to_frame("monate")
    .reorder_levels(["jahr", "krs", "fm", "egplus"])
    .sort_index()
    .reset_index()
)

df = df.replace({"/": pd.NA, "-": pd.NA})

df.jahr = df.jahr.astype(pd.Int64Dtype())
df.monate = df.monate.str.replace(",", ".").astype(pd.Float64Dtype())

df.to_parquet("data/processed/eg_dauer.parquet")


#
# Steuerkraft
#
df = pd.read_csv(
    steuer,
    encoding="latin-1",
    sep=";",
    skiprows=5,
    skipfooter=4,
    engine="python",
).iloc[1:, :]

df = (df
      .rename(columns={"Unnamed: 0": "jahr",
                       "Unnamed: 1": "rs",
                       "Unnamed: 2": "krs",
                       "Lohn- und Einkommensteuerpflichtige": "stpflichtige",
                       "Gesamtbetrag der Einkünfte": "einkuenfte",
                       "Lohn- und Einkommensteuer": "steuer",})
      .set_index(["jahr", "krs", "rs"])
      .replace({"-": pd.NA, ".": pd.NA}).astype(pd.Int64Dtype())
      .reset_index()
)

df.jahr = df.jahr.astype(pd.Int64Dtype())

df.einkuenfte *= 1000
df.steuer *= 1000

df["steuer_pc"] = df.steuer / df.stpflichtige

df.to_parquet("data/processed/steuern.parquet")


#
# Einwohnerzahlen
#
df = pd.read_csv(
    ewz,
    encoding="latin-1",
    sep=";",
    skiprows=5,
    skipfooter=4,
    engine="python",
)

df = (df
 .rename({"Unnamed: 0": "land"}, axis=1)
 .set_index(["land"])
 .rename_axis(axis=1, mapper="jahr")
 .rename(columns=lambda x: re.sub(r"31\.12\.", "", x))
 .stack()
 .to_frame("ewz")
 .reorder_levels(["jahr", "land"])
 .sort_index()
 .reset_index()
 .astype({"jahr": pd.Int64Dtype(), "ewz": pd.Int64Dtype()})
)

df.to_parquet("data/processed/ewz.parquet")