import sys
from pathlib import Path
import logging

from flask import Flask
import numpy as np
import pandas as pd
import geopandas as gpd
from dash import Dash, dcc, html, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# from data.sources import destatis_sources, bkg_source
from .colors import color_rgba
from .utils import cuyo, num

# import from config relatively, so it remains portable:
dashapp_rootdir = Path(__file__).resolve().parents[1]
sys.path.append(str(dashapp_rootdir))

# set up logging:
logging.basicConfig(
    level=logging.DEBUG,
    filename="elternsein.log",
    filemode="a",
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

    #
    # Background work used everywhere
    #
    color_dict = {
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
        'Thüringen': '#c49c94'
    }

    #
    # Births
    #

    # load data:
    data_gb = pd.read_parquet(dashapp_rootdir / "data/processed/geburten.parquet")
    data_gb = data_gb.groupby(["jahr", "land"]).geburten.sum().to_frame().reset_index()

    data_ewz = pd.read_parquet(dashapp_rootdir / "data/processed/ewz.parquet")

    # scale births by state population:
    data_gb = pd.merge(data_gb, data_ewz, on=["jahr", "land"])
    data_gb["geburten_pro_1000"] = data_gb.geburten / data_gb.ewz * 1000

    # define plot:
    plot_gb = go.Figure()

    for land, grp in data_gb.groupby("land"):
        plot_gb.add_trace(
            go.Scatter(
                x=grp.jahr,
                y=grp.geburten_pro_1000,
                mode="markers+lines",
                name=land,
                visible=(
                    True if land in ["Bayern", "Berlin"] else "legendonly"
                ),
                marker=dict(
                    color=color_dict.get(land, "black")
                )
            ),
        )

    plot_gb.update_layout(
        title="<b>Geburtenrate</b><br>pro 1.000 Einwohner",
        margin=dict(t=70, r=20, b=20, l=20),
        yaxis=dict(
            range=[
                data_gb.geburten_pro_1000.min() * 0.99,
                data_gb.geburten_pro_1000.max() * 1.01,
            ]
        ),
    )

    # package:
    fig_gb = dcc.Graph(id="fig_gb", figure=plot_gb)

    # =========================================================================

    #
    # recipients of Elterngeld
    #
    data_eg = pd.read_parquet(dashapp_rootdir / "data/processed/eg_empf.parquet")

    data_eg = data_eg.loc[data_eg.art.eq("Insgesamt")]
    data_eg = data_eg.loc[data_eg.fm.ne("Insgesamt")]

    data_eg = (
        data_eg.groupby(["jahr", "land", "fm", "art"])
        .sum()
        .drop("quartal", axis=1)
        .reset_index()
    )

    data_eg["grp_display"] = data_eg.apply(
        lambda row: f"{'Mütter' if row.fm=='weiblich' else 'Väter'} in {row.land}",
        axis=1,
    )

    data_eg = data_eg.sort_values(
        by=["jahr", "land", "fm"], ascending=[True, True, False]
    ).reset_index(drop=True)

    fm_line = {
        "weiblich": "solid",
        "männlich": "dash",
    }

    plot_eg = go.Figure()

    for var, grp in data_eg.groupby(["land", "fm"]):
        plot_eg.add_trace(
            go.Scatter(
                x=grp.jahr,
                y=grp.pers,
                mode="markers+lines",
                line=dict(dash=fm_line[var[1]], color=color_dict[var[0]]),
                name=var[0],
                showlegend=var[1] == "weiblich",
                legendgroup=var[0],
                visible=True if var[0] in ["Bayern","Berlin"] else "legendonly",
                customdata=grp.grp_display.values,
                hovertemplate="%{customdata}: %{y:f}<extra></extra>",
            )
        )

    plot_eg.update_layout(
        title="<b>Empfänger:innen von Elterngeld</b><br>aufgeschlüsselt nach Müttern und Vätern",
        hovermode="x unified",
        margin=dict(t=70, r=20, b=20, l=20),
        yaxis=dict(range=[0, data_eg.pers.max()], tickformat=".0f"),
        legend_tracegroupgap=0,
    )

    # package:
    fig_eg = dcc.Graph(id="fig_eg", figure=plot_eg)

    # =========================================================================

    #
    # relative EG recipients
    #

    # merge EG and birth data, scale EG numbers:
    data_egb = pd.merge(
        data_eg,
        data_gb[["jahr", "land", "geburten"]],
        on=["jahr", "land"],
        how="left"
    )
    data_egb["eg_rate"] = data_egb.pers / data_egb.geburten * 100

    # define plot:
    plot_egb = go.Figure()

    for var, grp in data_egb.groupby(["land", "fm"]):
        plot_egb.add_trace(
            go.Scatter(
                x=grp.jahr,
                y=grp.eg_rate,
                mode="markers+lines",
                line=dict(
                    dash=fm_line[var[1]],
                    color=color_dict[var[0]]
                ),
                name=var[0],
                showlegend=var[1]=="weiblich",
                legendgroup=var[0],
                visible=True if var[0] in ["Bayern", "Berlin"] else "legendonly",
                customdata=grp.grp_display.values,
                hovertemplate="%{customdata}: bei %{y:.1f}% der geborenen Kinder<extra></extra>",
            )
        )

    plot_egb.update_layout(
        title="<b>Empfänger:innen von Elterngeld als Anteil an den Geburten</b><br>aufgeschlüsselt nach Müttern und Vätern",
        hovermode="x unified",
        margin=dict(t=70, r=20, b=20, l=20),
        yaxis=dict(range=[0, 100]),
        legend_tracegroupgap=0,
    )

    # package:
    fig_egb = dcc.Graph(id="fig_egb", figure=plot_egb)

    # =========================================================================

    #
    # map: months of EG support
    #
    eg = pd.read_parquet(dashapp_rootdir / "data/processed/eg_dauer.parquet")
    gdf = gpd.read_parquet(dashapp_rootdir / "data/processed/vg250_krs.parquet")

    df = gpd.GeoDataFrame(
        pd.merge(
            eg, gdf[["ags", "geom"]],
            on="ags"
        ),
        geometry="geom"
    )


    plot_map_bezdauer, axs = plt.subplots(
        ncols=3,
        nrows=1,
        sharex=True, sharey=True,
    )

    plot_map_bezdauer.set_size_inches(20, 7.5)

    z_var = "monate"
    xfac_var = "fm"

    # die Selektion von egplus und jahr ist dann als interaktiver Teil realisiert:
    df_plot = df.query(
        'egplus == "Mit Elterngeld Plus"'
        'and jahr == 2023'
    )

    facet_var = "fm"
    facets = df_plot[facet_var].unique()

    cols = np.array([0, 1, 2])
    subpltcoord = cols

    # die drei Karten haben jeweils unterschiedliche Schwankungsbreiten und damit Farbskalen;
    # daher benutzen wir auch drei unterschiedliche Paletten, damit nicht der Eindruck von
    # Vergleichbarkeit entsteht:
    colorpalettes = [
        "viridis",
        "plasma",
        "cividis",
    ]

    for xy, facet in zip(subpltcoord, facets):

        df_facet = df_plot.loc[df_plot[facet_var].eq(facet)]

        x = xy
        df_facet.plot(
            ax=axs[x],
            column=z_var,
            legend=True,
            cmap=colorpalettes[x]
        )

        axs[x].set_title(facet)

    for ax in axs:
        ax.axis("off")

    buf = BytesIO()
    plot_map_bezdauer.savefig(buf, format="png")
    plot_map_bezdauer_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig_map_bezdauer = f"data:image/png;base64,{plot_map_bezdauer_data}"

    fig_map_bezdauer = html.Img(src=fig_map_bezdauer, style={"width": "100%"})

    # =========================================================================
    
    #
    # Map: income tax per capita
    #
    dfs = pd.read_parquet(dashapp_rootdir / "data/processed/steuern.parquet")
    # TODO interactive selection:
    dfs = dfs.query('jahr == 2019')

    dfs = dfs.loc[dfs.rs.str.len().le(5)]
    dfs["ags"] = dfs.rs.str.ljust(8, "0")

    gdf = gpd.read_parquet(dashapp_rootdir / "data/processed/vg250_krs.parquet")

    df = gpd.GeoDataFrame(
        pd.merge(
            dfs, gdf[["ags", "geom"]],
            on="ags"
        ),
        geometry="geom"
    ).drop("rs", axis=1)

    plot_map_taxes, ax = plt.subplots()

    plot_map_taxes.set_size_inches(10, 10)

    df.plot(
        ax=ax,
        column="steuer_pc",
        legend=True,
        cmap="viridis",
        vmax=12000,
    )

    ax.axis("off")
    ax.set_title("Steuerkraft 2019")

    buf = BytesIO()
    plot_map_taxes.savefig(buf, format="png")
    plot_map_taxes_data = "data:image/png;base64," + base64.b64encode(buf.getbuffer()).decode("ascii")

    fig_map_taxes = html.Img(src=plot_map_taxes_data, style={"width": "100%"})

    # =========================================================================
    
    #
    # tax level vs. months of EG support
    #
    df = pd.read_parquet(dashapp_rootdir / "data" / "processed" / "kreise_steuern_egdauer.parquet")

    # unnötige Einrückung in Kreisnamen entfernen:
    df.krs = df.krs.str.lstrip()

    # schönere Zahlendarstellung:
    df["steuer_pc_pretty"] = df.steuer_pc.apply(num)

    # Jahre sortieren:
    df = df.sort_values(["jahr", "ags"]).reset_index(drop=True)

    # die Ost-West-Markierung:
    df["ostwest"] = df.ags.apply(lambda x: "Ost" if int(x[0:2]) > 10 else "West")

    # auf ein Jahr festlegen:
    df = df.loc[
        # df.jahr.eq(2019)
        df.fm.eq("Insgesamt")
        & df.egplus.eq("Mit Elterngeld Plus")
    ]

    # Farben:
    colormap = {
        "Ost": "#ff0000",
        "West": "#66ccff",
    }

    plot_taxes_egdauer = go.Figure()

    for jahr, grp in df.groupby("jahr"):

        for ostwest, lgrp in grp.groupby("ostwest"):

            plot_taxes_egdauer.add_trace(
                go.Scatter(
                    x=lgrp.steuer_pc,
                    y=lgrp.monate,
                    visible=jahr==2016,
                    mode="markers",
                    marker=dict(color=color_rgba(colormap[ostwest], .5), size=10, line=dict(width=1, color="black")),
                    customdata=lgrp[["krs", "steuer_pc_pretty", "monate"]],
                    hovertemplate="<b>%{customdata[0]}:</b><br><br>Steuerkraft: €%{customdata[1]}<br>durchschnittlich %{customdata[2]} Monate EG<extra></extra>",
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
                {"visible": [False] * len(plot_taxes_egdauer.data)},  # alle ausblenden...
                {"title": title}
            ]
        )
        # ...außer diesen:
        for idx in cuyo(plot_taxes_egdauer, str(jahr)):
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

    plot_taxes_egdauer.update_layout(
        plot_bgcolor="rgba(0,0,0, .05)",
        width=800,
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

    fig_taxes_egdauer = dcc.Graph(id="fig_taxes_egdauer", figure=plot_taxes_egdauer)


    #
    # Prose
    # =========================================================================
    with open(dashapp_rootdir / "elternsein" / "prose" / "map_egdauer.md") as file:
        prose_egdauer = file.read()
    
    with open(dashapp_rootdir / "elternsein" / "prose" / "map_taxes.md") as file:
        prose_taxes = file.read()
    
    with open(dashapp_rootdir / "elternsein" / "prose" / "sct_egdauer_taxes.md") as file:
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
                        style={
                            "backgroundColor": "rgba(50,50,255, .1)",
                            "paddingTop": "50px",
                        },
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
                        style={
                            "backgroundColor": "rgba(50,50,255, .1)",
                            "paddingTop": "50px",
                        },
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
                        style={
                            "backgroundColor": "rgba(50,50,255, .1)",
                            "paddingTop": "50px",
                        },
                    ),
                    # map - how long parents got EG on average:
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Markdown(prose_egdauer),
                                xs={"size": 12},
                                lg={"size": 8, "offset": 2},
                            )
                        ],
                        style={
                            "backgroundColor": "rgba(50,50,255, .1)",
                            "paddingTop": "50px",
                        }
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [fig_map_bezdauer],
                                xs={"size": 12},
                                lg={"size": 10, "offset": 1},
                            ),
                        ],
                        style={
                            "backgroundColor": "rgba(50,50,255, .1)",
                            "paddingTop": "50px",
                        },
                    ),
                    # map - income tax across Germany:
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Markdown(prose_taxes),
                                xs={"size": 12},
                                lg={"size": 8, "offset": 2},
                            )
                        ],
                        style={
                            "backgroundColor": "rgba(50,50,255, .1)",
                            "paddingTop": "50px",
                        }
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [fig_map_taxes],
                                xs={"size": 12},
                                lg={"size": 8, "offset": 2},
                            ),
                        ],
                        style={
                            "backgroundColor": "rgba(50,50,255, .1)",
                            "paddingTop": "50px",
                        },
                    ),
                    # taxes versus months of EG support:
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Markdown(prose_taxes_egdauer),
                                xs={"size": 12},
                                lg={"size": 8, "offset": 2},
                            )
                        ],
                        style={
                            "backgroundColor": "rgba(50,50,255, .1)",
                            "paddingTop": "50px",
                        }
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [fig_taxes_egdauer],
                                xs={"size": 12},
                                lg={"size": 8, "offset": 2},
                            ),
                        ],
                        style={
                            "backgroundColor": "rgba(50,50,255, .1)",
                            "paddingTop": "50px",
                        },
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
