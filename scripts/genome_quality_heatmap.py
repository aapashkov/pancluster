#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: genome_quality_heatmap.py PREFIX [PREFIX ...]

Create a heatmap comparing genome quality of several genomes and print it in SVG
format to stdout. For each given PREFIX, this script reads PREFIX.bbstats.json
and PREFIX.buscolite.json, both of which are produced by genome_quality.py.
Specify LABELS environment variable as a comma separated list of labels for
each prefix to use instead of the file stems. Set TITLE env variable for plot
title

example: genome_quality_heatmap.py prefix1 prefix2 prefix3 > heatmap.svg"""

import json
import os
import re
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def main() -> int:
    """Driver code."""

    # Setting contrained and tight layout improves final layout
    warnings.filterwarnings(
        "ignore", "This figure was using constrained_layout==True"
    )

    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    files = [Path(file).resolve() for file in sys.argv[1:]]
    title = os.environ.get("TITLE", "")
    label_var = os.environ.get("LABELS")
    labels = (
        label_var.split(",") if label_var is not None
        else [file.name for file in files]
    )

    # Populate data dictionary for heatmap
    data_dict = {}

    for file in files:
        data_dict[file.name] = {}

        # Add contiguity metrics to data dictionary
        with open(f"{file}.bbstats.json", encoding="utf8") as handle:
            bbstats = json.load(handle)

        data_dict[file.name]["Número de scaffolds"] = bbstats["scaffolds"]
        data_dict[file.name]["Longitud total (Mpb)"] = (
            round(bbstats["scaf_bp"] / 1_000_000, 2)
        )
        # BBStats reports N50 in the L50 key
        data_dict[file.name]["N50 de scaffolds (Mpb)"] = (
            round(bbstats["scaf_L50"] / 1_000_000, 2)
        )

        # Add completeness metrics to data dictionary
        busco_metrics = [
            ["total", "BUSCOs completos (%)"],
            ["complete", "BUSCOs de copia única (%)"],
            ["duplicated", "BUSCOs duplicados (%)"],
            ["missing", "BUSCOs ausentes (%)"],
        ]
        busco_status = (
            pd.read_csv(
                f"{file}.buscolite.tsv", sep="\t", header=None, comment="#",
                names=["busco", "status", "sequence", "score", "length"]
            )
            [["busco", "status"]]
            .drop_duplicates()
            .set_index("busco")["status"]
        )
        n_buscos = len(busco_status)
        busco_counts = busco_status.value_counts().to_dict()

        # Compute metrics as percentages
        for metric_id, metric_name in busco_metrics:
            if metric_id == "total":
                metric_value = n_buscos - busco_counts.get("missing", 0)
            else:
                metric_value = busco_counts.get(metric_id, 0)

            metric_percentage = round((metric_value / n_buscos) * 100, 2)
            data_dict[file.name][metric_name] = metric_percentage

    # Real data is used for annotations, but values are scaled 0-1 for colors
    real_data = pd.DataFrame(data_dict).T
    real_data.index = labels
    data = real_data / real_data.max()
    real_data = real_data.apply(np.vectorize(
        lambda number: str(int(number)) if number.is_integer() else str(number)
    ))

    # For some columns, lower values are better
    lower = [
        "Número de scaffolds",
        "BUSCOs duplicados (%)",
        "BUSCOs ausentes (%)"
    ]
    data[lower] = data.apply(
        lambda x: (x - x.max()) / (x.min() - x.max())
    )[lower].fillna(1)
    data = data ** 3

    # Create plot
    fig, ax = plt.subplots(figsize=(6, len(files) + 2), constrained_layout=True)
    sns.heatmap(
        data, square=True, ax=ax, cbar=False, cmap="Blues",
        annot=real_data, linewidths=2, vmin=0.0, vmax=1.35, fmt=""
    )
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(sys.stdout, format="svg", transparent=True) # type: ignore

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
