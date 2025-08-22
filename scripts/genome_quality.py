#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: genome_quality.py DB FNA FAA OUTDIR

Runs a quality analysis of an input FNA genome and its associated FAA proteome.
Uses a BUSCO database stored in DB and saves results to OUTDIR. Uses Fusarium
graminearum as default species; change it by setting the SPECIES environment
variable.

example: genome_quality.py hypocreales_odb10/ genome.fna proteins.faa results/"""

import atexit
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

    buscolite = check_exec("buscolite")
    stats = check_exec("stats.sh")
    species = os.environ.get("SPECIES", "fusarium")

    if len(sys.argv) != 5:
        print(__doc__, file=sys.stderr)
        return 1

    db = Path(sys.argv[1]).resolve()
    genome = Path(sys.argv[2]).resolve()
    proteins =  Path(sys.argv[3]).resolve()
    outdir = Path(sys.argv[4]).resolve()
    if not outdir.exists():
        print(f"error: {outdir} does not exist", file=sys.stderr)
        return 1

    # Setup tmp directory
    tmp = Path(tempfile.mkdtemp(prefix=".tmp", dir=".")).resolve()
    atexit.register(shutil.rmtree, tmp)
    os.chdir(tmp)

    # Run BUSCOlite
    cmd = [
        buscolite, "-i", proteins, "-o", genome.stem, "-m", "proteins",
        "-l", db, "-s", species, "-c", "1"
    ]
    subprocess.run(cmd, check=True, stdout=sys.stderr)

    # Run stats.sh
    cmd = [stats, f"in={genome}", "format=8"]
    with open(f"{genome.stem}.bbstats.json", "w", encoding="utf8") as handle:
        subprocess.run(cmd, check=True, stdout=handle)

    # Move results out of tmp directory
    for suffix in ["bbstats.json", "buscolite.tsv", "buscolite.json"]:
        shutil.move(f"{genome.stem}.{suffix}", outdir)

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
