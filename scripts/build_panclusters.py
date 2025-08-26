#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: build_panclusters.py DIR OUTPREFIX

Run a pancluster analysis from a given BiG-SCAPE results DIR and save it to
OUTPREFIX. Two files are produced: OUTPREFIX.tsv containing a presence absence
matrix, and OUTPREFIX.json listing gene names referred by each gene family in
OUTPREFIX.tsv. This script will always use the most recent network found in the
BIGSCAPE directory. Use JOBS environment variable for parallelization.

example: build_panclusters.py gcfs/ results/panclusters"""

import atexit
import functools
import json
import multiprocessing
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Tuple

import pandas as pd


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


def single_pancluster(
    family: str,
    clustering: pd.Series,
    annotations: pd.Series,
    bigscape: Path,
    proteinortho: str,
) -> Tuple[dict, pd.DataFrame]:
    """Build a single pancluster for a given `family` in the `clustering`
    mapping, using files found in the `bigscape` directory, with the
    `proteinortho` executable. The `annotations` mapping is used to identify
    the name of the genome a BGC belongs to."""

    # Get BGCs that belong to input family and copy them to current dir (tmp)
    bgcs = clustering[clustering == family].index
    bgcs.map(lambda bgc: shutil.copyfile(
        str(bigscape/"cache"/"fasta"/f"{bgc}.fasta"), f"{bgc}.faa"
    ))

    # If the family contains only one BGC, create a file with a single column
    if len(bgcs) == 1:
        with open(f"{bgcs[0]}.faa", encoding="utf8") as handle:
            genes = [
                [line[1:].strip()] for line in handle if line.startswith(">")
            ]

        # Prepare outputs
        mapper = dict(zip(
            [f"c{family}_g{idx}" for idx in range(len(genes))], genes
        ))
        pancluster = pd.DataFrame({
            fam: {f"{annotations[bgcs[0]]}": 1} for fam in mapper
        })
        pancluster.index.name = "accession"

        return mapper, pancluster

    # Run Proteinortho on the BGCs
    cmd = [proteinortho, f"-project={family}", "-clean", "-cpus=1", "-singles"]
    subprocess.run(cmd + (bgcs+".faa").tolist(), check=True, stdout=sys.stderr)

    # Prepare outputs
    pancluster = pd.read_csv(f"{family}.proteinortho.tsv", sep="\t")
    pancluster = pancluster[pancluster.columns[3:]]
    pancluster.columns = annotations[pancluster.columns.str[:-4]]
    pancluster.columns.name = "accession"
    pancluster.index = f"c{family}_g" + pancluster.index.astype(str)
    pancluster: pd.DataFrame = pancluster.applymap(
        lambda x: [] if x == "*" else x.split(",")
    ) # type: ignore
    mapper = pancluster.apply(
        lambda series: sum(series, start=[]), axis=1
    ).to_dict()
    pancluster: pd.DataFrame = pancluster.applymap(bool).astype(int).T # type: ignore

    # Delete tmp files
    for bgc in bgcs:
        for file in Path(".").glob(f"{bgc}.*"):
            os.remove(file)
    for file in Path(".").glob(f"{family}.*"):
        os.remove(file)

    return mapper, pancluster


def main() -> int:
    """Driver code."""

    proteinortho = check_exec("proteinortho")
    jobs = int(os.environ.get("JOBS", "1"))

    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 1

    bigscape = Path(sys.argv[1]).resolve()
    outprefix = Path(sys.argv[2]).resolve()
    if not outprefix.parent.exists():
        print(f"error: {outprefix.parent} does not exist", file=sys.stderr)
        return 1

    # Setup tmp directory
    tmp = Path(tempfile.mkdtemp(prefix=".tmp", dir=".")).resolve()
    atexit.register(shutil.rmtree, tmp)
    os.chdir(tmp)

    # Get the most recent BGC network
    most_recent_network = sorted((bigscape / "network_files").glob("*"))[-1]

    # Maps BGCs to GCFs
    clustering = pd.read_csv(
        most_recent_network/"mix"/"mix_clustering_c0.30.tsv",
        sep="\t", dtype=str, index_col="#BGC Name"
    )["Family Number"]

    # Maps BGCs to genomes
    annotations = pd.read_csv(
        most_recent_network/"Network_Annotations_Full.tsv",
        sep="\t", dtype=str, index_col="BGC"
    )["Organism"]

    # Remove MIBiG BGCs from clustering
    clustering = clustering[~clustering.index.str.startswith("BGC0")]

    # Build pancluster for each family
    unique_families = clustering.unique()
    pancluster_func = functools.partial(
        single_pancluster,
        clustering=clustering,
        annotations=annotations,
        bigscape=bigscape,
        proteinortho=proteinortho
    )
    with multiprocessing.Pool(jobs) as pool:
        mappers, panclusters = zip(*pool.map(pancluster_func, unique_families))

    # Create json output file mapping BGC gene families to genes
    json_contents = {}
    for dictionary in mappers:
        json_contents.update(dictionary)
    with open(f"{outprefix}.json", "w", encoding="utf") as handle:
        json.dump(json_contents, handle, indent=2)

    # Create csv output file with presence absence of BGC families
    csv_contents = pd.concat(panclusters, axis=1, sort=True)
    csv_contents = csv_contents.fillna(0).astype(int)
    csv_contents.index.name = "accession"
    csv_contents.to_csv(f"{outprefix}.csv")

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
