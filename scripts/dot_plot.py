#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: dot_plot.py REFERENCE QUERY

Create a dot plot between the REFERENCE and QUERY genomes in FASTA format, and
print it to stdout in SVG format.

example: dot_plot.py reference.fasta query.fasta > aln.svg"""

import io
import re
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def check_exec(*executables: str):
    """Find and return an executable from input, showing error if none is
    found."""

    choice = None
    for executable in executables:
        if shutil.which(executable) is not None:
            choice = executable
            break
    if choice is None:
        print(
            f"error: could not find an executable for '{executables[0]}'",
            file=sys.stderr
        )
        sys.exit(1)
    else:
        return choice


def main() -> int:
    """Driver code."""

    minimap2 = check_exec("minimap2")

    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 1

    ref = Path(sys.argv[1]).resolve()
    qry = Path(sys.argv[2]).resolve()

    # Run alignment
    process = subprocess.run(
        [minimap2, "-x", "asm5", ref, qry], check=True, stdout=subprocess.PIPE
    )

    # Parse output
    cols = [
        "qname", "qlen", "qstart", "qend", "strand", "tname", "tlen", "tstart",
        "tend","nmatch","alen","mapq"
    ]
    paf = pd.read_csv(
        io.StringIO(process.stdout.decode()),
        sep="\t", header=None, usecols=range(12), names=cols
    )

    # Sort reference (t) contigs by size and query (q) contigs by alignment
    paf = paf.sort_values("tstart")
    paf = paf.sort_values(["tlen", "mapq"], ascending=False)

    # Get start positions of reference (t) contigs and query (q) contigs
    tcontigs = (
        paf[["tname", "tlen"]]
        .drop_duplicates()
        .set_index("tname")["tlen"]
        .shift(1).fillna(0).cumsum()
    )
    qcontigs = (
        paf[["qname", "qlen"]]
        .drop_duplicates()
        .set_index("qname")["qlen"]
        .shift(1).fillna(0).cumsum()
    )

    # Sum start positions to alignment coordinates to get real (r) positions
    paf["rqstart"] = paf["qstart"] + paf["qname"].map(qcontigs)
    paf["rqend"] = paf["qend"] + paf["qname"].map(qcontigs)
    paf["rtstart"] = paf["tstart"] + paf["tname"].map(tcontigs)
    paf["rtend"] = paf["tend"] + paf["tname"].map(tcontigs)

    # Switch reference start and end when strand is '-' (reverse)
    paf.loc[paf["strand"] == "-", ["rqstart", "rqend"]] = paf.loc[
        paf["strand"] == "-", ["rqend", "rqstart"]
    ].values

    # Compute total length of both genomes
    qlength = paf[["qname", "qlen"]].drop_duplicates()["qlen"].sum()
    tlength = paf[["tname", "tlen"]].drop_duplicates()["tlen"].sum()

    # Create figure
    fig, ax = plt.subplots(figsize=(3, 3))
    colors = {
        "-": (0.00392156862745098, 0.45098039215686275, 0.6980392156862745),
        "+": (0.8352941176470589, 0.3686274509803922, 0.0)
    }

    # Set color for strand, and transparency for mapping quality
    for _, row in paf.iterrows():
        x = [row["rtstart"], row["rtend"]]
        y = [row["rqstart"], row["rqend"]]
        alpha = row["mapq"] / 60
        color = colors[row["strand"]]
        ax.plot(x, y, color=color, alpha=alpha, lw=0.75, marker=".", ms=1)

    # Set ticks to contig edges
    ax.tick_params(width=0.25)
    ax.set_xticks(tcontigs.values)
    ax.set_yticks(qcontigs.values)
    ax.set_xticklabels(
        [""] * (len(ax.get_xticks()) - 1) + [f"{tlength / 1e6:.1f}Mb"],
        fontsize=4
    )
    ax.set_yticklabels(
        [""] * (len(ax.get_yticks()) - 1) + [f"{qlength / 1e6:.1f}Mb"],
        fontsize=4, rotation=90
    )
    ax.set_xlim(0, tlength)
    ax.set_ylim(0, qlength)
    ax.set_xlabel(f"{ref.stem} (ref.)", fontsize=6)
    ax.set_ylabel(f"{qry.stem} (qry.)", fontsize=6)

    # Final adjustments and saving to stdout
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(visible=True, lw=0.25, color="#EEEEEE")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(sys.stdout, format="svg") # type: ignore

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
