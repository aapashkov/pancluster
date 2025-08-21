#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: annotate_genome.py FASTA OUTDIR

Annotate an eukaryotic genome FASTA and save results to OUTDIR. Uses Fusarium
graminearum as default species; change it by setting the SPECIES environment
variable.

example: SPECIES=neurospora annotate_genome.py input.fasta output/"""

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

    funannotate = check_exec("funannotate")
    tantan = check_exec("tantan")
    species = os.environ.get("SPECIES", "fusarium")

    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 1

    file = Path(sys.argv[1]).resolve()
    outdir = Path(sys.argv[2]).resolve()
    if not outdir.exists():
        print(f"error: {outdir} does not exist", file=sys.stderr)
        return 1

    # Setup tmp directory
    tmp = Path(tempfile.mkdtemp(prefix=".tmp", dir=".")).resolve()
    atexit.register(shutil.rmtree, tmp)
    os.chdir(tmp)

    # Mask genome
    with open("masked.fna", "w", encoding="utf8") as handle:
        subprocess.run([tantan, file], check=True, stdout=handle)

    # Run annotation
    subprocess.run(
        [
            funannotate, "predict", "-i", "masked.fna", "-o", file.stem,
            "-s", file.stem, "--augustus_species", species,
            "--busco_seed_species", species, "--force", "--cpus", "1",
            "--no-progress", "--tmpdir", "tmp", "--header_length", "1000"
        ],
        check=True,
        stdout=sys.stderr
    )

    # Move out of tmp directory
    shutil.move(file.stem, outdir/file.stem)

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
