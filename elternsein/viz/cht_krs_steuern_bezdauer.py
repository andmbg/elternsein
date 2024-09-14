import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

from elternsein.utils import num, cuyo
from elternsein.colors import color_rgba
from ..i18n import translate as t

base_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(base_dir))

# from ...data.sources import destatis_sources

processed_dir = base_dir / "data" / "processed"


def cht_krs_steuern_bezdauer():

    df = pd.read_parquet(processed_dir / "kreise_steuern_egdauer.parquet")

    # unnötige Einrückung in Kreisnamen entfernen:
    df.krs = df.krs.str.lstrip()

    # schönere Zahlendarstellung:
    df["steuer_pc_pretty"] = df.steuer_pc.apply(num)

    # Jahre sortieren:
    df = df.sort_values(["jahr", "ags"]).reset_index(drop=True)

    # die Ost-West-Markierung:
    df["ostwest"] = df.ags.apply(lambda x: t("Ost") if int(x[0:2]) > 10 else t("West"))

    # auf ein Jahr festlegen:
    df = df.loc[
        # df.jahr.eq(2019)
        df.fm.eq("Insgesamt")
        & df.egplus.eq("Mit Elterngeld Plus")
    ]

    # Farben:
    colormap = {
        t("Ost"): "#ff0000",
        t("West"): "#66ccff",
    }

    fig = go.Figure()

    for jahr, grp in df.groupby("jahr"):

        for ostwest, lgrp in grp.groupby("ostwest"):

            fig.add_trace(
                go.Scatter(
                    x=lgrp.steuer_pc,
                    y=lgrp.monate,
                    visible=jahr==2016,
                    mode="markers",
                    marker=dict(color=color_rgba(colormap[ostwest], .5), size=10, line=dict(width=1, color="black")),
                    customdata=lgrp[["krs", "steuer_pc_pretty", "monate"]],
                    hovertemplate=(
                        "<b>%{customdata[0]}:</b><br><br>"
                        f"{t('Steuerkraft')}" + ": €%{customdata[1]}<br>"
                        f"{t('durchschnittlich')}" + " %{customdata[2]} "
                        f"{t('Monate Elterngeld')}<extra></extra>"
                    ),
                    name=lgrp.ostwest.iloc[0] + " " + str(jahr)
                )
            )

    steps = []
    for i, jahr in enumerate(df.jahr.unique()):
        title = f"<b>Steuerkraft und Bezugsdauer beim Elterngeld</b><br>im Jahr {jahr}"

        # jeder Step definiert den Plot-Titel und welche Traces sichtbar sind
        step = dict(
            method="update",
            args=[
                {"visible": [False] * len(fig.data)},  # alle ausblenden...
                {"title": title}
            ]
        )
        # ...außer diesen:
        for idx in cuyo(fig, str(jahr)):
            step["args"][0]["visible"][idx] = True
        
        steps.append(step)

    sliders = [
        dict(
            active=0,
            currentvalue={"prefix": "Jahr "},
            pad={"t": 0},
            steps=steps,
            transition={"duration": 300, "easing": "cubic-in-out"},
        )
    ]

    xticks = [5000, 10000, 15000, 20000]
    yticks = list(range(23))

    fig.update_layout(
        paper_bgcolor="rgba(255,255,255, 0)",
        plot_bgcolor="rgba(255,255,255, 0)",
        # width=800,
        height=600,
        margin=dict(t=50, r=10, b=20, l=50),
        xaxis=dict(
            tickvals=xticks,
            ticktext=[num(x) + " €" for x in xticks],
            range=[0, 20000],
        ),
        yaxis=dict(
            tickvals=yticks,
            ticktext=[str(x) + " Mon." for x in yticks],
            range=[14, 23],
        ),
        legend=dict(
            x=.7, y=.8,
            bgcolor="rgba(0,0,0,0)"
        ),
        sliders=sliders
    )

    return fig
