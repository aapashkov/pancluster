#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: bar_counter.py FILE [TITLE]

Create a simple bar plot by counting strings in FILE with optional TITLE string
and print it to stdout in SVG format.

example: bar_counter.py fsp.txt "forma specialis" > bars.svg"""

import re
import sys
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns


def main() -> int:
    """Driver code."""

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(__doc__, file=sys.stderr)
        return 1

    file = Path(sys.argv[1])
    title = "" if len(sys.argv) == 2 else sys.argv[2]

    with open(file, encoding="utf8") as handle:
        counts = Counter(line.strip() for line in handle)

    labels, values = map(list, zip(*sorted(counts.items(), key=lambda x: x[0])))

    fig, ax = plt.subplots(figsize=(3, 3))
    ax.bar(
        x=labels,
        height=values,
        color=sns.color_palette("colorblind"),
        ec="black"
    )

    for index, value in enumerate(values):
        ax.annotate(str(value), (index, value + 2), ha="center", va="center")

    ax.set_xlabel(title)
    ax.set_ylabel("genomas")
    ax.tick_params("x", labelrotation=90)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(sys.stdout, format="svg", transparent=True)

    return 0


if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(main())
