#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: pancluster_network.py BIGSCAPE ORGANISM ORGANISM [ORGANISM ...]

Plot the GCF network taken from a BIGSCAPE output directory for a given set of
at least two ORGANISMs and print it to stdout in svg format. This script will
always use the most recent BiG-SCAPE network. Up to nine ORGANISMs are
supported.

example: pancluster_network.py gcfs organism1 organism2 > network.svg"""

import atexit
import functools
import multiprocessing
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Tuple, Iterable

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.lines import Line2D
from scipy.optimize import curve_fit


def setup_tmp():
    """Sets up and changes to temporary directory."""

    tmp = Path(tempfile.mkdtemp(prefix=".tmp", dir="."))
    atexit.register(shutil.rmtree, tmp)
    os.chdir(tmp)


def estimate_heaps_law(
    data, iters: int = 1000, random_state: int = 0
) -> Tuple[float, float]:
    """Compute Heaps' equation parameters using `iters` iterations of random
    permutations of `data` using the `random_state` seed. Returns two floats:
    kappa and alpha."""

    rng = np.random.default_rng(random_state)
    y = np.atleast_2d(data)
    y = y[y.sum(1) > 0]
    n_samples = y.shape[0]
    y = np.array([rng.permutation(y) for _ in range(iters)])
    y = np.diff(y.cumsum(1).astype(bool).sum(2), axis=1, prepend=0).flatten()
    x = np.tile(np.arange(1, n_samples+1), iters)

    try:
        kappa, alpha = curve_fit(
            lambda array, kappa, alpha: kappa * array**(-alpha),
            xdata=x,
            ydata=y,
            p0=[10, 2]
        )[0]
    except RuntimeError:
        kappa, alpha = np.nan, np.nan

    return kappa, alpha


def run_pancluster(
    bgcs: Iterable[str], bigscape: Path,
    iters: int = 1000, random_state: int = 0
):
    """Build a pancluster from BGCs and return Heaps' law alpha parameter."""

    tmp = Path(tempfile.mkdtemp(dir="."))
    files: list[Path] = []

    for bgc in bgcs:
        file = (bigscape.parent.parent/"cache"/"fasta"/f"{bgc}.fasta").resolve()
        shutil.copyfile(file, tmp/f"{bgc}.faa")
        files.append(tmp/f"{bgc}.faa")

    cmd = [
        "proteinortho", f"-project={tmp.name}", "-cpus=1", "-silent", "-clean",
        "-singles", f"-temp={tmp}"
    ] + files
    subprocess.run(
        cmd, check=True, stdout=sys.stderr, stderr=subprocess.DEVNULL
    )

    df = pd.read_csv(f"{tmp.name}.proteinortho.tsv", sep="\t")[[
        file.name for file in files
    ]].apply(lambda series: series.str.count(":gid::pid:"))
    alpha = estimate_heaps_law(df, iters, random_state)[1]

    return alpha


def main() -> int:
    """Driver code."""

    jobs = int(os.environ.get("JOBS", "1"))
    n_cols = int(os.environ.get("NCOLS", "14"))
    l_cols = int(os.environ.get("LCOLS", "4"))

    if len(sys.argv) < 4 or len(sys.argv) > 11:
        print(__doc__, file=sys.stderr)
        return 1

    # Get most recent BiG-SCAPE output
    bigscape = sorted(
        Path(sys.argv[1]).resolve().rglob("Network_Annotations_Full.tsv")
    )[-1].parent
    organisms = sys.argv[2:]

    setup_tmp()

    # Load annotations file and filter it to requested genomes and MIBiG BGCs
    annotations = pd.read_csv(
        bigscape/"Network_Annotations_Full.tsv", sep="\t", index_col="BGC"
    )
    annotations = annotations[
        annotations["Organism"].isin(organisms) |
        annotations.index.str.startswith("BGC0")
    ]

    # Load clustering file and merge it with annotations on common index
    clustering = pd.read_csv(
        bigscape/"mix"/"mix_clustering_c0.30.tsv", sep="\t",
        index_col="#BGC Name"
    )["Family Number"]
    annotations = annotations.merge(
        clustering, left_index=True, right_index=True
    )

    # Remove families consisting only by MIBiG genomes
    for bgc_family in annotations["Family Number"].unique():
        subset: pd.DataFrame = annotations[
            annotations["Family Number"] == bgc_family
        ]
        if not (subset["Organism"].isin(organisms)).sum():
            annotations.drop(index=subset.index, inplace=True)

    clustering = annotations.pop("Family Number")

    # Ensure all supplied organisms exist
    missing_organisms = set(organisms) - set(annotations["Organism"].unique())
    if missing_organisms:
        print(f"error: missing {missing_organisms}", file=sys.stderr)
        return 1

    # Replace all MIBiG genomes with "MIBiG"
    annotations.loc[
        annotations[~annotations["Organism"].isin(organisms)].index, "Organism"
    ] = "MIBiG"

    # Load networks file and filter to organisms of interest
    networks = pd.read_csv(
        bigscape/"mix"/"mix_c0.30.network", sep="\t",
        usecols=["Clustername 1", "Clustername 2", "Jaccard index"]
    )
    networks = networks[
        networks["Clustername 1"].isin(annotations.index) &
        networks["Clustername 2"].isin(annotations.index)
    ]

    # Create graph
    graph = nx.Graph()
    for bgc in annotations.index:
        graph.add_node(
            bgc,
            bgc_class=annotations.loc[bgc, "BiG-SCAPE class"],
            bgc_family=clustering.loc[bgc]
        )
    for _, edge in networks.iterrows():
        graph.add_edge(
            edge["Clustername 1"],
            edge["Clustername 2"],
            weight=edge["Jaccard index"]
        )

    # Start figure
    n_rows = int(np.ceil(
        ((clustering.value_counts() != 1).sum() + len(organisms)) / n_cols
    ))
    fig, axs = plt.subplots(
        n_rows, n_cols, layout="tight", figsize=(n_cols, n_rows * 1.1)
    )

    # Order BGC families first by size, then by number
    bgc_families = (
        clustering.value_counts().reset_index()
        .sort_values(["count", "Family Number"], ascending=[False, True])
        ["Family Number"].values
    )
    markers = dict(zip(
        "PKSI NRPS PKS-NRP_Hybrids Terpene Others PKSother Saccharides RiPPs".split(),
        list("PsXoD^vh")
    ))
    first_singleton_axis = None

    # Run pancluster analysis on every family with at least two BGCs
    bgcs_by_family = filter(lambda x: len(x) > 1, [
        clustering[clustering == fam].index for fam in bgc_families
    ])
    with multiprocessing.Pool(jobs) as pool:
        func = functools.partial(run_pancluster, bigscape=bigscape)
        if jobs > 1:
            alphas = pool.map(func, bgcs_by_family)
        else:
            alphas = list(map(func, bgcs_by_family))

    # For each ax
    for index, ax in enumerate(axs.flatten()):
        ax: plt.Axes # pyright: ignore[reportPrivateImportUsage]

        ax.set_axis_off()
        ax.set_aspect("equal")
        ax.set_xlim(-1.25, 1.25)
        ax.set_ylim(-1.25, 1.25)

        # Avoid overflow of BGC family series
        if index >= len(bgc_families):
            break

        # Query subgraph for BGC family
        bgc_family = bgc_families[index]
        bgcs = clustering[clustering == bgc_family].index
        genomes = annotations.loc[bgcs, "Organism"].values
        bgc_classes = annotations.loc[bgcs, "BiG-SCAPE class"]

        if len(bgcs) != 1:
            alpha = alphas[index]
            subgraph: nx.Graph = nx.subgraph(graph, bgcs)
            pos = nx.circular_layout(subgraph)
            x, y = zip(*pos.values())
            weights = [edge[2]["weight"] for edge in subgraph.edges(data=True)]

            nx.draw_networkx_edges(
                subgraph, pos, ax=ax, alpha=weights, width=.8
            )
            sns.scatterplot(
                x=x, y=y, ax=ax, legend=False, style=bgc_classes,
                markers=markers, palette=sns.color_palette("colorblind"),
                hue=genomes, hue_order=["MIBiG"] + organisms, ec="black"
            )
            ax.set_title(f"F{bgc_family}\n$\\alpha={alpha:.2f}$", fontsize=10)

        # Identify last ax to plot singletons
        elif len(bgcs) == 1 and first_singleton_axis is None:
            first_singleton_axis = index

    # Plot singletons
    if first_singleton_axis is not None:
        remaining_axs = axs.flatten()[first_singleton_axis:][:len(organisms)]
        for index, ax in enumerate(remaining_axs):
            ax: plt.Axes # pyright: ignore[reportPrivateImportUsage]

            organism = organisms[index]
            singletons = {key: 0 for key in markers}
            singletons.update(annotations.loc[
                annotations[annotations["Organism"] == organism].index,
                "BiG-SCAPE class"
            ].value_counts())

            x=[-1.05, -1.05, -1.05, -1.05,  0.60,  0.60,  0.60,  0.60]
            y=[ 0.90,  0.30, -0.30, -0.90,  0.90,  0.30, -0.30, -0.90]

            sns.scatterplot(
                x=x, y=y, ax=ax, legend=False, style=list(markers),
                markers=markers, palette=sns.color_palette("colorblind"),
                hue=np.repeat(organism, 8), hue_order=["MIBiG"] + organisms,
                ec="black"
            )
            for idx, count in enumerate(singletons.values()):
                ax.text(
                    x[idx] + .2, y[idx], f"×{count}", ha="left", va="center",
                    size=7
                )

    # Create legend manually
    palette = sns.color_palette("colorblind")
    handles = [
        Line2D(
            [], [], color=fc, marker="o", label=label, lw=0, mec="black", mew=.5
        ) for label, fc in zip(["MIBiG"] + organisms, palette)
    ]
    handles += [
        Line2D(
            [], [], marker=marker, color="black", label=label, lw=0
        ) for label, marker in markers.items()
    ]

    fig.legend(handles=handles, loc="lower right", ncols=l_cols)
    fig.savefig(sys.stdout, format="svg", transparent=True)

    return 0


if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(main())
