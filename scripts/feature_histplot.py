#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: feature_histplot.py ACCESSIONS VARIABLES

Create a histplot from a file with ACCESSIONS and a table of VARIABLES.

example: feature_histplot.py accessions.csv panclusters.csv > plot.svg"""

import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def main() -> int:
    """Driver code."""

    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 1

    fsp = pd.read_csv(sys.argv[1], index_col=0).iloc[:, 0].dropna()
    counts = fsp.value_counts()
    fsp = fsp[fsp.isin(counts[counts > 1].index)]
    variables = pd.read_csv(sys.argv[2], index_col=0)
    accessions = list(set(fsp.index) & set(variables.index))
    fsp = fsp.loc[accessions].sort_values()
    variables = variables.loc[fsp.index].T
    variables = variables.groupby(
        variables.index.str.split("_").str[0]
    ).sum().astype(bool).astype(int).T.sum(axis=1)

    plot_data = [variables[fsp[fsp == fs].index] for fs in fsp.unique()]
    fig, ax = plt.subplots(figsize=(3, 3))

    ax.hist(
        plot_data,
        stacked=True,
        color=sns.color_palette("colorblind"),
        label=fsp.unique().tolist(),
        ec="black"
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlabel(Path(sys.argv[2]).stem)
    ax.set_ylabel("genomas")
    fig.tight_layout()
    fig.savefig(sys.stdout, format="svg", transparent=True)

    return 0


if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(main())
