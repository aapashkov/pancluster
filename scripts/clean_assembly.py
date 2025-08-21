#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: clean_assembly.py FASTA NANOPORE

Removes repetitive contigs, sorts by size and renames contigs, and deletes
haplotigs from an assembly. Requires passing a file with NANOPORE reads.

example: clean_assembly.py input.fasta reads.fastq.gz > output.fasta"""

import atexit
import gzip
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


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

    funannotate = check_exec("funannotate")
    minimap2 = check_exec("minimap2")
    pbcstat = check_exec("pbcstat")
    calcuts = check_exec("calcuts")
    split_fa = check_exec("split_fa")
    purge_dups = check_exec("purge_dups")
    get_seqs = check_exec("get_seqs")

    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 1

    file = Path(sys.argv[1]).resolve()
    nanopore = Path(sys.argv[2]).resolve()

    # Setup tmp directory
    tmp = Path(tempfile.mkdtemp(prefix=".tmp", dir=".")).resolve()
    atexit.register(shutil.rmtree, tmp)
    os.chdir(tmp)

    # First round of cleaning
    subprocess.run(
        [funannotate, "clean", "-i", file, "-o", "cleaned.fna"],
        check=True, stdout=sys.stderr
    )

    # Remove haplotigs
    # See https://github.com/dfguan/purge_dups?tab=readme-ov-file#--pipeline-guide
    with gzip.open("cleaned.paf.gz", "wt") as handle:
        subprocess.run(
            [minimap2, "-x", "map-ont", "cleaned.fna", nanopore],
            check=True, stdout=handle
        )

    subprocess.run([pbcstat, "cleaned.paf.gz"], check=True, stdout=sys.stderr)

    with open("cutoffs", "w", encoding="utf8") as handle:
        subprocess.run([calcuts, "PB.stat"], check=True, stdout=handle)

    with open("cleaned.split", "w", encoding="utf8") as handle:
        subprocess.run([split_fa, "cleaned.fna"], check=True, stdout=handle)

    with gzip.open("cleaned.split.self.paf.gz", "wt") as handle:
        subprocess.run(
            [minimap2, "-x", "asm5", "-DP", "cleaned.split", "cleaned.split"],
            check=True, stdout=handle
        )
    
    with open("dups.bed", "w", encoding="utf8") as handle:
        subprocess.run(
            [
                purge_dups, "-2", "-T", "cutoffs", "-c", "PB.base.cov",
                "cleaned.split.self.paf.gz"
            ],
            check=True, stdout=handle
        )

    subprocess.run(
        [get_seqs, "-e", "dups.bed", "cleaned.fna"],
        check=True, stdout=sys.stderr
    )

    # Sort by size and rename contigs
    subprocess.run(
        [
            funannotate, "sort", "-i", "hap.fa", "-o", "final.fna",
            "--minlen", "0"
        ],
        check=True, stdout=sys.stderr
    )
    with open("final.fna", encoding="utf8") as handle:
        shutil.copyfileobj(handle, sys.stdout)

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
