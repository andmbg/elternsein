import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

base_dir = Path(__file__).resolve().parents[2]
sys.path.append(base_dir)

from data.sources import destatis_sources


def cht_eg_births():

    # Elterngeld data:
    eg = pd.read_parquet(destatis_sources["eg_empf"]["processed_file"])
    eg = eg.reset_index(drop=True)

    lastyear = eg.jahr.max()
    entries_lastyear = eg[["jahr"]].value_counts().sort_index().iloc[-1]
    entries_penultim = eg[["jahr"]].value_counts().sort_index().iloc[-2]

    if entries_lastyear < entries_penultim:
        eg = eg.loc[eg.jahr.ne(lastyear)]

    eg = eg.loc[eg.art.eq("Insgesamt")]
    eg = eg.loc[eg.fm.ne("Insgesamt")]

    eg = eg.groupby(["jahr", "land", "fm", "art"]).sum().drop("quartal", axis=1).reset_index()

    eg["grp_display"] = eg.apply(
        lambda row: f"{'Mütter' if row.fm=='weiblich' else 'Väter'} in {row.land}",
        axis=1
    )

    eg = eg.sort_values(by=["jahr", "land", "fm"], ascending=[True, True, False]).reset_index(drop=True)
    land_clr = {
        'Schleswig-Holstein': '#1f77b4',
        'Hamburg': '#ff7f0e',
        'Niedersachsen': '#2ca02c',
        'Bremen': '#d62728',
        'Nordrhein-Westfalen': '#9467bd',
        'Hessen': '#8c564b',
        'Rheinland-Pfalz': '#e377c2',
        'Baden-Württemberg': '#7f7f7f',
        'Bayern': '#bcbd22',
        'Saarland': '#17becf',
        'Berlin': '#aec7e8',
        'Brandenburg': '#ffbb78',
        'Mecklenburg-Vorpommern': '#98df8a',
        'Sachsen': '#ff9896',
        'Sachsen-Anhalt': '#c5b0d5',
        'Thüringen': '#c49c94',
    }

    # Birth data:
    gb = pd.read_parquet(destatis_sources["geburten"]["processed_file"])
    gb = gb.groupby(["jahr", "land"]).geburten.sum().to_frame().reset_index()

    ewz = pd.read_parquet(destatis_sources["ewz"]["processed_file"])

    gb = pd.merge(gb, ewz, on=["jahr", "land"])
    gb["geburten_pro_1000"] = gb.geburten / gb.ewz * 1000

    egb = pd.merge(
        eg,
        gb[["jahr", "land", "geburten"]],
        on=["jahr", "land"],
        how="left"
    )
    egb["eg_rate"] = egb.pers / egb.geburten * 100

    fm_line = {
        "weiblich": "solid",
        "männlich": "dash",
    }

    fig = go.Figure()

    for var, lgrp in egb.groupby(["land", "fm"]):
        fig.add_trace(
            go.Scatter(
                x=lgrp.jahr,
                y=lgrp.eg_rate,
                mode="markers+lines",
                line=dict(
                    dash=fm_line[var[1]],
                    color=land_clr[var[0]]
                ),
                name=var[0],
                showlegend=var[1]=="weiblich",
                legendgroup=var[0],
                visible=True if var[0] == "Berlin" else "legendonly",
                customdata=lgrp.grp_display.values,
                hovertemplate="%{customdata}: bei %{y:.1f}% der geborenen Kinder<extra></extra>"
            )
        )

    fig.update_layout(
        hovermode="x unified",
        # width=1000,
        height=800,
        margin=dict(t=20, r=20, b=20, l=20),
        yaxis=dict(range=[0, egb.eg_rate.max()])
    )

    return fig
