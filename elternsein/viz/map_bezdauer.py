from matplotlib import pyplot as plt
import pandas as pd
import geopandas as gpd
import numpy as np

from data.sources import destatis_sources, bkg_source


def map_bezdauer():
    eg = pd.read_parquet(destatis_sources["eg_dauer"]["processed_file"])
    gdf = gpd.read_parquet(bkg_source["processed_file"])

    df = gpd.GeoDataFrame(
        pd.merge(
            eg, gdf[["ags", "geom"]],
            on="ags"
        ),
        geometry="geom"
    )

    fig, axs = plt.subplots(
        ncols=3,
        nrows=1,
        sharex=True, sharey=True,
    )

    fig.set_size_inches(20, 7.5)

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
    
    return fig, axs
