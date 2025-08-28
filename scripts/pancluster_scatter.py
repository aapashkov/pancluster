#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: pancluster_scatter.py JSON ANNOTATIONS

Create a scatterplot from a panclusters JSON dataset and a BiG-SCAPE full
network ANNOTATIONS tsv file.

example: pancluster_scatter.py panclusters.json Network_Annotations_Full.tsv > plot.svg"""

import json
import re
import sys
from typing import Tuple, Dict, List

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from adjustText import adjust_text
from scipy.optimize import curve_fit


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


def main() -> int: # pylint: disable=too-many-arguments, too-many-locals, too-many-statements
    """Driver code."""

    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 1

    with open(sys.argv[1], encoding="utf8") as handle:
        panclusters: Dict[str, List[str]] = json.load(handle)
    annotations = pd.read_csv(sys.argv[2], sep="\t", index_col=0)["Organism"]

    current_bgc_family: str = ""
    current_gcf_length: int = 0
    data_dict = {}
    bgc_families: List[str] = []
    gcf_lengths: List[int] = []
    kappas: List[float] = []
    alphas: List[float] = []
    full_data_dict: Dict[str, Dict[str, int]] = {}

    for full_gene_family, gene_list in panclusters.items():
        bgc_family, gene_family = full_gene_family.split("_")
        full_data_dict[full_gene_family] = {}
        if current_bgc_family == "" or bgc_family != current_bgc_family:
            if current_bgc_family:
                df = pd.DataFrame(data_dict).fillna(0).astype(int)
                if len(df) > 1:
                    kappa, alpha = estimate_heaps_law(df)
                    if not np.isnan(kappa) and not np.isnan(alpha):
                        bgc_families.append(current_bgc_family[1:])
                        kappas.append(kappa)
                        alphas.append(alpha)
                        gcf_lengths.append(current_gcf_length)
            data_dict = {}
            current_bgc_family = bgc_family
            current_gcf_length = 0
        data_dict[gene_family] = {}
        current_gcf_length += 1
        for gene in gene_list:
            bgc = gene.split("_ORF", 1)[0]
            full_data_dict[full_gene_family][annotations[bgc]] = 1
            data_dict[gene_family][bgc] = 1

    full_data = pd.DataFrame(full_data_dict).fillna(0).astype(int).sort_index()
    full_alpha = estimate_heaps_law(full_data, iters=100)[1]

    fig, ax = plt.subplots(figsize=(6, 6))
    scatter = ax.scatter(
        alphas, kappas, c=gcf_lengths, ec="black", alpha=0.9, cmap="Blues_r"
    )
    fig.colorbar(
        scatter, ax=ax, shrink=0.4, label="número de familias génicas"
    )
    ax.axvline(x=full_alpha, ls="--", color="black", lw=0.75)
    ax.text(
        x=full_alpha,
        y=ax.get_ylim()[1] - 5,
        s=f"{full_alpha:.4f}",
        rotation="vertical",
        ha="right"
    )
    xticks = ax.get_xticks()
    if 1 not in xticks:
        xticks = np.append(xticks, 1)
        xticks.sort()
        ax.set_xticks(xticks[1:-1])

    labels = []
    paragraph = []
    for index, alpha in enumerate(alphas):
        if alpha < 1.0:
            paragraph.append(f"{len(labels)}: f{bgc_families[index]}")
            labels.append(plt.text(
                x=alpha, y=kappas[index], s=str(len(labels)), color="firebrick",
                ha="center", va="center", size="xx-small", weight="bold",
            ))

    ax.set_xlabel("alpha")
    ax.set_ylabel("kappa")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    adjust_text(
        labels,
        arrowprops={
            "arrowstyle": "-", "color": "red", "shrinkA": 0, "shrinkB": 0,
            "lw": 0.5, "ls": ":", "alpha": 0.5
        },
        ax=ax,
        expand_points=(2.55, 2.7),
    )
    for index, line in enumerate(paragraph):
        ax.text(
            ax.get_xlim()[1] - 2,
            ax.get_ylim()[1] - (index / 2) - 1,
            line,
            size="xx-small"
        )
    fig.savefig(sys.stdout.buffer, transparent=True, format="pdf")

    return 0


if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(main())
