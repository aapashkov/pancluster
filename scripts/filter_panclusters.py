#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: filter_panclusters.py FILE INPREFIX ANNOTATIONS OUTPREFIX

Filter panclusters from INPREFIX to genomes listed in FILE by reading the
BiG-SCAPE network ANNOTATIONS file and saving results to OUTPREFIX.

example: filter_panclusters.py accessions.txt panclusters Network_Annotations_Full.tsv panclusters_filtered"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd


def main() -> int:
    """Driver code."""

    if len(sys.argv) != 5:
        print(__doc__, file=sys.stderr)
        return 1

    file = Path(sys.argv[1])
    inprefix = Path(sys.argv[2])
    annotations = Path(sys.argv[3])
    outprefix = Path(sys.argv[4])
    if not outprefix.parent.exists():
        print(f"error: {outprefix.parent} does not exist", file=sys.stderr)
        return 1

    with open(file, encoding="utf8") as handle:
        accessions = {acc.strip() for acc in handle}

    bgc_genomes = pd.read_csv(
        annotations, sep="\t", index_col="BGC"
    )["Organism"]

    df = pd.read_csv(f"{inprefix}.csv", index_col=0).loc[sorted(accessions)]
    with open(f"{inprefix}.json", encoding="utf8") as handle:
        mapper: Dict[str, List[str]] = json.load(handle)

    outmapper: Dict[str, List[str]] = {}
    for gcf, genes in mapper.items():
        valid_genes = [
            gene for gene in genes if
            bgc_genomes[gene.split("_ORF", 1)[0]] in accessions
        ]
        if valid_genes:
            outmapper[gcf] = valid_genes

    df.to_csv(f"{outprefix}.csv")
    with open(f"{outprefix}.json", "w", encoding="utf8") as handle:
        json.dump(outmapper, handle, indent=2)

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
