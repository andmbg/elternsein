import sys
from pathlib import Path
from matplotlib import pyplot as plt
import pandas as pd
import geopandas as gpd

base_dir = Path(__file__).resolve().parents[2]
sys.path.append(base_dir)

from ...data.sources import destatis_sources, bkg_source


def map_steuern():
    dfs = pd.read_parquet(destatis_sources["steuern"]["processed_file"])
    # interaktiv:
    dfs = dfs.query('jahr == 2019')

    dfs = dfs.loc[dfs.rs.str.len().le(5)]
    dfs["ags"] = dfs.rs.str.ljust(8, "0")

    gdf = gpd.read_parquet(bkg_source["processed_file"])

    df = gpd.GeoDataFrame(
        pd.merge(
            dfs, gdf[["ags", "geom"]],
            on="ags"
        ),
        geometry="geom"
    ).drop("rs", axis=1)

    fig, ax = plt.subplots()

    df.plot(
        ax=ax,
        column="steuer_pc",
        legend=True,
        cmap="viridis",
        vmax=12000,
    )

    ax.axis("off")
    ax.set_title("Steuerkraft 2019")

    return fig, ax
