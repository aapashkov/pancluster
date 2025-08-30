#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: phylogenomic_tree.py ACCESSIONS PROTEINS BUSCO FASCONCAT [PROTSUFFIX] [BUSCOSUFFIX]

Create a phylogenomic tree from an ACCESSIONS file listing per comma-separated
column the accession, its name, and its group. The first accession in the list
will be used as the phylogenetic outgroup. The script will look up the
accessions recursively in the PROTEINS directory for files ending with '.faa'
(change PROTSUFFIX if it has a different extension), as well as BUSCOlite
results in the BUSCO directory for files ending with '.buscolite.tsv' (change
BUSCOSUFFIX if it has a different extension). You will need to also provide
the path to FASconCAT_v1.11.pl script with FASCONCAT. The resulting tree is
plotted to stdout in svg format. Set JOBS environment variable for
parallelization.

example: phylogenomic_tree.py accessions.csv proteins/ busco/ FASconCAT_v1.11.pl > tree.svg"""

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
from typing import List

import pandas as pd
import phytreeviz
import seaborn as sns
from Bio import SeqIO
from Bio.Phylo import Newick, NewickIO


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


def read_buscolite(file: Path):
    """Read a BUSCOlite file, get complete BUSCOs and store them in
    output dictionary.
    """

    busco = pd.read_csv(
        file, sep="\t", comment="#", header=None, usecols=range(3),
        names=["id", "status", "seq"], index_col=0
    )

    return busco[busco["status"] == "complete"]["seq"].to_dict()


def align_and_trim(
    busco_entry: tuple, accessions: pd.DataFrame, muscle: str, gblocks: str
):
    """Run alignment on a BUSCO entry of a busco dataframe."""

    buscoid: str
    proteins: pd.Series
    buscoid, proteins = busco_entry

    # Create faa file for the BUSCO entry
    with open(f"{buscoid}.faa", "w", encoding="utf8") as output:
        for genome, protein in proteins.items():
            file = accessions.loc[str(genome), "file"]
            with open(file, encoding="utf8") as handle: # type: ignore
                for record in SeqIO.parse(handle, "fasta"):
                    if record.id == protein:
                        print(f">{genome}\n{record.seq}", file=output)
                        break

    # Align sequences
    subprocess.run(
        [muscle, "-in", f"{buscoid}.faa", "-out", f"{buscoid}.aln"],
        check=True,
        stdout=sys.stderr
    )

    # Perform alignment trimming, ignore check as exit code of 1 is common
    subprocess.run(
        [gblocks, f"{buscoid}.aln", "-t", "p"],
        check=False,
        stdout=sys.stderr
    )

    # Rename for fasconcat and remove extra files
    os.rename(f"{buscoid}.aln-gb", f"{buscoid}.fas")
    for extension in ["aln", "aln-gb.htm", "faa"]:
        os.remove(f"{buscoid}.{extension}")


def main() -> int:
    """Driver code."""

    jobs = int(os.environ.get("JOBS", "1"))

    # Check executable dependencies
    muscle = check_exec("muscle3", "muscle")
    iqtree = check_exec("iqtree2", "iqtree")
    gblocks = check_exec("Gblocks")

    if len(sys.argv) < 5 or len(sys.argv) > 7:
        print(__doc__, file=sys.stderr)
        return 1

    accfile = Path(sys.argv[1]).resolve()
    proteins = Path(sys.argv[2]).resolve()
    busco = Path(sys.argv[3]).resolve()
    fasconcat = Path(sys.argv[4]).resolve()
    protsuffix = sys.argv[5] if len(sys.argv) > 5 else ".faa"
    buscosuffix = sys.argv[6] if len(sys.argv) > 6 else ".buscolite.tsv"

    # Setup tmp directory
    tmp = Path(tempfile.mkdtemp(prefix=".tmp", dir="."))
    atexit.register(shutil.rmtree, tmp)
    os.chdir(tmp)

    # Copy fasconcat executable into tmp
    shutil.copyfile(fasconcat, "FASconCAT_v1.11.pl")

    # Load accessions list
    accessions = pd.read_csv(
        accfile, header=None, index_col=0,
        names=["accession", "name", "group"]
    )
    outgroup: str = accessions.index[0]

    # Get filenames of proteins
    accessions["file"] = {
        file.name.removesuffix(protsuffix): file
        for file in proteins.rglob(f"*{protsuffix}")
        if file.name.removesuffix(protsuffix) in accessions.index
    }

    # Load BUSCOlite files and get all common complete BUSCOs
    buscodf = pd.DataFrame({
        file.name.removesuffix(buscosuffix): read_buscolite(file)
        for file in busco.rglob(f"*{buscosuffix}")
        if file.name.removesuffix(buscosuffix) in accessions.index
    })[accessions.index].dropna()

    # Run alignment and trimming on all BUSCO families
    functor = functools.partial(
        align_and_trim, accessions=accessions, muscle=muscle, gblocks=gblocks
    )
    with multiprocessing.Pool(jobs) as pool:
        mapper = pool.imap_unordered if jobs > 1 else map
        list(mapper(functor, buscodf.iterrows()))

    # Concatenate trimmed alignments
    subprocess.run(
        ["perl", "FASconCAT_v1.11.pl", "-s", "-n"],
        check=True,
        stdout=sys.stderr
    )
    os.rename("FcC_smatrix.fas", "FcC_smatrix.faa")

    # Create RAxML partition file by parsing FcC_info.xls
    with (
        open("FcC_info.xls", encoding="utf8") as inp,
        open("FcC_smatrix.partitions", "w", encoding="utf8") as out
    ):
        table_started = False
        index = 0
        for line in inp:
            contents = line.strip().split("\t")

            if len(contents) == 1:
                continue
            if not table_started:
                table_started = True
                continue
            if contents[0] == "FcC_smatrix.fas":
                break

            index += 1
            print(
                f"PROTEIN, part{index} = {contents[3].replace(' => ', '-')}",
                file=out
            )

    # Build tree
    cmd = [
        iqtree, "-s", "FcC_smatrix.faa", "-m", "TEST", "-B", "10000",
        "-T", str(jobs), "-p", "FcC_smatrix.partitions", "-o", outgroup
    ]
    subprocess.run(cmd, check=True, stdout=sys.stderr)

    # Load tree for plotting
    with open("FcC_smatrix.partitions.treefile", encoding="utf8") as handle:
        tree = next(NewickIO.parse(handle))

    # Rename terminals to add bold and italics
    terminals: List[Newick.Clade] = tree.get_terminals()
    label_dict = {}
    for terminus in terminals:
        original = f"{terminus.name}"
        name = f"{terminus.name}".replace("_", r"\_")
        name = "".join(["$\\bf{", name, "}$ "])
        species = f'{accessions.loc[f"{terminus.name}", "name"]}'
        species = species.replace("-", "\\text{-}").replace("_", r"\_")
        species = "".join([
            "$\\it{", species.replace(" ", "}$ $\\it{"), "}$"
        ])
        name = "".join([name, species])
        label_dict[original] = name
        terminus.name = name

    label_mapper = pd.Series(label_dict)

    # Create tree
    tv = phytreeviz.TreeViz(tree, height=0.3, width=6)
    tv.show_scale_bar()

    # Add highlights and annotations
    groups = accessions["group"]
    unique_groups = sorted(set(groups).difference({"External"}))
    colors = sns.color_palette("colorblind", len(unique_groups))
    for index, group in enumerate(unique_groups):
        query = label_mapper[groups[groups == group].index].tolist()
        orient = "vertical" if len(query) > 2 else "horizontal"
        tv.highlight(query, colors[index], alpha=0.2, area="full") # type: ignore
        tv.annotate(
            query, group, line_color=colors[index], text_color=colors[index], # type: ignore
            text_orientation=orient, text_size=14, text_kws={"weight": "bold"},
            align=True
        )

    # Add confidence and create output plot
    tv.show_confidence(
        xpos="right", size=12, weight="bold",
        label_formatter=lambda v: "" if v == 100 else f"{round(v)}"
    )
    fig = tv.plotfig()
    fig.savefig(sys.stdout, format="svg", transparent=True)

    return 0


if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(main())
