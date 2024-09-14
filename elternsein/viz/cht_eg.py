import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

base_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(base_dir))

from data.sources import destatis_sources
from ..i18n import translate_series, translate as t


def cht_eg():

    eg = pd.read_parquet(destatis_sources["eg_empf"]["processed_file"])
    eg = eg.reset_index(drop=True)
    eg.land = translate_series(eg.land)

    lastyear = eg.jahr.max()
    entries_lastyear = eg[["jahr"]].value_counts().sort_index().iloc[-1]
    entries_penultim = eg[["jahr"]].value_counts().sort_index().iloc[-2]

    if entries_lastyear < entries_penultim:
        eg = eg.loc[eg.jahr.ne(lastyear)]

    eg = eg.loc[eg.art.eq("Insgesamt")]
    eg = eg.loc[eg.fm.ne("Insgesamt")]

    eg = eg.groupby(["jahr", "land", "fm", "art"]).sum().drop("quartal", axis=1).reset_index()

    eg["grp_display"] = eg.apply(
        lambda row: f"{t('Mütter') if row.fm=='weiblich' else t('Väter')} in {row.land}",
        axis=1
    )

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

    fm_line = {
        "weiblich": "solid",
        "männlich": "dash",
    }

    fig = go.Figure()

    for var, lgrp in eg.groupby(["land", "fm"]):
        fig.add_trace(
            go.Scatter(
                x=lgrp.jahr,
                y=lgrp.pers,
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
                hovertemplate="%{customdata}: %{y:f}<extra></extra>"
            )
        )

    fig.update_layout(
        paper_bgcolor="rgba(255,255,255, 0)",
        plot_bgcolor="rgba(255,255,255, 0)",
        hovermode="x unified",
        # width=1000,
        height=550,
        margin=dict(t=50, r=20, b=20, l=20),
        yaxis=dict(
            range=[0, eg.pers.max()],
            tickformat=".0f"
        ),
        title="Empfänger:innen von Elterngeld"
    )

    return fig
