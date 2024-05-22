import sys
from pathlib import Path
import logging

# from flask import Flask
import numpy as np
import pandas as pd
import geopandas as gpd
from dash import Dash, dcc, html#, Input, Output, State, callback, dash_table
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
    taxes_bitmap = "data:image/png;base64," + base64.b64encode(buf.getbuffer()).decode("ascii")
    fig_map_taxes = html.Img(src=taxes_bitmap, style={"width": "100%"})

    # tax level vs. months of EG support
    fig_taxes_egdauer = dcc.Graph(id="fig_taxes_egdauer", figure=viz.cht_krs_steuern_bezdauer())


    #
    # Prose
    # =========================================================================
    with open(base_dir / "elternsein" / "prose" / "map_egdauer.md") as file:
        prose_egdauer = file.read()
    
    with open(base_dir / "elternsein" / "prose" / "map_taxes.md") as file:
        prose_taxes = file.read()
    
    with open(base_dir / "elternsein" / "prose" / "sct_egdauer_taxes.md") as file:
        prose_taxes_egdauer = file.read()

    #
    # Layout
    # =========================================================================

    app.layout = html.Div(
        [
            dbc.Container(
                style={"paddingTop": "50px"},
                children=[
                    # dcc.Store(id="keystore", data=[]),
                    
                    # births figure:
                    dbc.Row(
                        [
                            dbc.Col(
                                [fig_gb],
                                xs={"size": 12},
                                lg={"size": 8, "offset": 2},
                            ),
                        ],
                        class_name="para mt-4",
                    ),
                    
                    # Elterngeld figure:
                    dbc.Row(
                        [
                            dbc.Col(
                                [fig_eg],
                                xs={"size": 12},
                                lg={"size": 8, "offset": 2},
                            ),
                        ],
                        class_name="para mt-4",
                    ),

                    # relative EG figure:
                    dbc.Row(
                        [
                            dbc.Col(
                                [fig_egb],
                                xs={"size": 12},
                                lg={"size": 8, "offset": 2},
                            ),
                        ],
                        class_name="para mt-4",
                    ),

                    # map - how long parents got EG on average:
                    # prose:
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Markdown(prose_egdauer),
                                xs={"size": 12},
                                lg={"size": 8, "offset": 2},
                            )
                        ],
                        class_name="para mt-4",
                    ),
                    # figure:
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    fig_map_bezdauer
                                ],
                                xs={"size": 12},
                                lg={"size": 10, "offset": 1},
                            ),
                        ],
                        class_name="para mt-1",
                    ),

                    # map - income tax across Germany:
                    # prose:
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Markdown(prose_taxes),
                                xs={"size": 12},
                                lg={"size": 8, "offset": 2},
                            )
                        ],
                        class_name="para mt-4",
                    ),
                    # figure:
                    dbc.Row(
                        [
                            dbc.Col(
                                [fig_map_taxes],
                                xs={"size": 12},
                                lg={"size": 8, "offset": 2},
                            ),
                        ],
                        class_name="para mt-1",
                    ),

                    # taxes versus months of EG support:
                    # prose:
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Markdown(prose_taxes_egdauer),
                                xs={"size": 12},
                                lg={"size": 8, "offset": 2},
                            )
                        ],
                        class_name="para mt-4",
                    ),
                    # figure:
                    dbc.Row(
                        [
                            dbc.Col(
                                [fig_taxes_egdauer],
                                xs={"size": 12},
                                lg={"size": 8, "offset": 2},
                            ),
                        ],
                        class_name="para mt-1",
                    ),
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
