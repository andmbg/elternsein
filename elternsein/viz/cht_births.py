import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

# base_dir = Path(__file__).resolve().parents[2]
# sys.path.append(str(base_dir))

from data.sources import destatis_sources
from ..i18n import translate_series


def cht_births():

    gb = pd.read_parquet(destatis_sources["geburten"]["processed_file"])
    gb = gb.groupby(["jahr", "land"]).geburten.sum().to_frame().reset_index()

    ewz = pd.read_parquet(destatis_sources["ewz"]["processed_file"])

    gb = pd.merge(gb, ewz, on=["jahr", "land"])
    gb["geburten_pro_1000"] = gb.geburten / gb.ewz * 1000

    # i18n:
    gb["land"] = translate_series(gb.land)

    fig = go.Figure()

    for land, lgrp in gb.groupby("land"):
        fig.add_trace(
            go.Scatter(
                x=lgrp.jahr,
                y=lgrp.geburten_pro_1000,
                mode="markers+lines",
                name=land
            ),
        )

    fig.update_layout(
        # width=1000,
        height=800,
        margin=dict(t=20, r=20, b=20, l=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255, 0)",
    )

    return fig
