import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

# base_dir = Path(__file__).resolve().parents[2]
# sys.path.append(base_dir)

from data.sources import destatis_sources
from ..i18n import translate as t, translate_series

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

    eg.land = translate_series(eg.land)

    eg = eg.sort_values(by=["jahr", "land", "fm"], ascending=[True, True, False]).reset_index(drop=True)
    land_clr = {
        t('Schleswig-Holstein'): '#1f77b4',
        t('Hamburg'): '#ff7f0e',
        t('Niedersachsen'): '#2ca02c',
        t('Bremen'): '#d62728',
        t('Nordrhein-Westfalen'): '#9467bd',
        t('Hessen'): '#8c564b',
        t('Rheinland-Pfalz'): '#e377c2',
        t('Baden-Württemberg'): '#7f7f7f',
        t('Bayern'): '#bcbd22',
        t('Saarland'): '#17becf',
        t('Berlin'): '#aec7e8',
        t('Brandenburg'): '#ffbb78',
        t('Mecklenburg-Vorpommern'): '#98df8a',
        t('Sachsen'): '#ff9896',
        t('Sachsen-Anhalt'): '#c5b0d5',
        t('Thüringen'): '#c49c94',
    }

    # Birth data:
    gb = pd.read_parquet(destatis_sources["geburten"]["processed_file"])
    gb = gb.groupby(["jahr", "land"]).geburten.sum().to_frame().reset_index()
    gb.land = translate_series(gb.land)

    ewz = pd.read_parquet(destatis_sources["ewz"]["processed_file"])
    ewz.land = translate_series(ewz.land)

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

    # i18n
    egb.land = translate_series(egb.land)
    egb.grp_display = translate_series(egb.grp_display)

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
                hovertemplate="%{customdata}: " + t("bei %{y:.1f}% der geborenen Kinder<extra></extra>")
            )
        )

    fig.update_layout(
        paper_bgcolor="rgba(255,255,255, 0)",
        plot_bgcolor="rgba(255,255,255, 0)",
        hovermode="x unified",
        # width=1000,
        height=800,
        margin=dict(t=20, r=20, b=20, l=20),
        yaxis=dict(range=[0, egb.eg_rate.max()])
    )

    return fig
