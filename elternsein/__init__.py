import sys
from pathlib import Path
import logging

# from flask import Flask
import numpy as np
import pandas as pd
import geopandas as gpd
from dash import Dash, dcc, html  # , Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import base64
from io import BytesIO

base_dir = Path(__file__).resolve().parents[1]
sys.path.append(base_dir)

# from data.sources import destatis_sources, bkg_source
from .colors import color_rgba
from .utils import cuyo, num
from . import viz

# set up logging:
logging.basicConfig(
    level=logging.DEBUG,
    filename=str(base_dir / "logs" / "elternsein.log"),
    filemode="w",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
root_logger = logging.getLogger()
root_logger.handlers[0].setFormatter(formatter)


def init_dashboard(flask_app, route):

    app = Dash(
        __name__,
        server=flask_app,
        routes_pathname_prefix=route,
        # relevant for standalone launch, not used by main flask app:
        external_stylesheets=[dbc.themes.FLATLY],
    )

    #
    # Plotly elements
    # (defined outside the layout, so it stays legible)
    # =========================================================================

    # Births:
    fig_gb = dcc.Graph(id="fig_gb", figure=viz.cht_births())

    # recipients of Elterngeld:
    fig_eg = dcc.Graph(id="fig_eg", figure=viz.cht_eg())

    # EG recipients vs. births:
    fig_egb = dcc.Graph(id="fig_egb", figure=viz.cht_eg_births())

    # map: months of EG support:
    fig, axs = viz.map_bezdauer()
    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    plot_map_bezdauer_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    bezdauer_bitmap = f"data:image/png;base64,{plot_map_bezdauer_data}"
    fig_map_bezdauer = html.Img(src=bezdauer_bitmap, style={"width": "100%"})

    # map: taxes:
    fig, ax = viz.map_steuern()
    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    taxes_bitmap = "data:image/png;base64," + base64.b64encode(buf.getbuffer()).decode(
        "ascii"
    )
    fig_map_taxes = html.Img(src=taxes_bitmap, style={"width": "100%"})

    # tax level vs. months of EG support
    fig_taxes_egdauer = dcc.Graph(
        id="fig_taxes_egdauer", figure=viz.cht_krs_steuern_bezdauer()
    )

    #
    # Prose
    # =========================================================================
    with open(base_dir / "elternsein" / "prose" / "geburten.md") as file:
        md_geburten = dcc.Markdown(file.read())

    with open(base_dir / "elternsein" / "prose" / "eg_empf.md") as file:
        md_eg_empf = dcc.Markdown(file.read())

    with open(base_dir / "elternsein" / "prose" / "egb.md") as file:
        md_egb = dcc.Markdown(file.read())

    with open(base_dir / "elternsein" / "prose" / "eg_dauer.md") as file:
        md_egdauer = dcc.Markdown(file.read())

    with open(base_dir / "elternsein" / "prose" / "taxes.md") as file:
        md_taxes = dcc.Markdown(file.read())

    with open(base_dir / "elternsein" / "prose" / "taxes_egdauer.md") as file:
        md_taxes_egdauer = dcc.Markdown(file.read())

    #
    # Layout
    # =========================================================================

    # abbreviate stuff:
    def para(content, class_name: str = "para mt-4"):
        out = dbc.Row(
            [
                dbc.Col(
                    [content],
                    xs={"size": 12},
                    lg={"size": 8, "offset": 2},
                ),
            ],
            class_name=class_name,
        )
        return out


    app.layout = html.Div(
        [
            dbc.Container(
                style={"paddingTop": "50px"},
                children=[
                    # dcc.Store(id="keystore", data=[]),
                    # births
                    para(md_geburten),
                    para(fig_gb),
                    # Elterngeld:
                    para(md_eg_empf),
                    para(fig_eg),
                    # relative EG:
                    para(md_egb),
                    para(fig_egb),
                    # map - how long parents got EG on average:
                    para(md_egdauer),
                    para(fig_map_bezdauer),
                    # map - income tax across Germany:
                    para(md_taxes),
                    para(fig_map_taxes),
                    # taxes versus months of EG support:
                    para(md_taxes_egdauer),
                    para(fig_taxes_egdauer),
                ],
            )
        ]
    )

    # init_callbacks(app, data_bund, data_raw)

    return app


# def init_callbacks(app, data_bund, data_raw):

# DEBUG: display sunburst clickdata:
# @app.callback(
#     Output("location", "children"),
#     Input("fig-sunburst", "clickData")
# )
# def update_location(clickdata):
#     return(sunburst_location(clickdata))
# ---------------------------------

# Update Presence chart
# @app.callback(Output("fig-key-presence", "figure"),
#               Input("fig-sunburst", "clickData"),
#               Input("table-textsearch", "derived_viewport_data"),
#               Input("tabs", "active_tab"))
# def update_presence_chart(keypicker_parent, table_data, active_tab):
#     """
#     Presence chart
#     """
#     if active_tab == "keypicker":
#         key = sunburst_location(keypicker_parent)

#         if key == "root" or key is None:  # just special syntax for when parent is None
#             child_keys = data_bund.loc[
#                 data_bund.parent.eq("------")
#                 ].key.unique()
#         else:
#             child_keys = data_bund.loc[data_bund.parent == key].key.unique(
#             )
#         selected_keys = child_keys

#     elif active_tab == "textsearch":
#         selected_keys = []
#         for element in table_data:
#             selected_keys.append(element["key"])

#     colormap = {k: grp.color.iloc[0]
#                 for k, grp in data_bund.groupby("key")}

#     fig = get_presence_chart(data_bund, selected_keys, colormap)

#     return (fig)
