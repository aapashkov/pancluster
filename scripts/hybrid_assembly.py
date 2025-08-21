#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: hybrid_assembly.py (masurca | spades) (denovo | scaffold) LONG SHORT [SHORT2]

Perform hybrid assembly using MaSuRCA or SPAdes, with a de novo or scaffold
approach, of LONG Nanopore and (optionally paired) SHORT read data. Final
assembly is printed to stdout in fasta format.

example: hybrid_assembly.py masurca denovo long.fq.gz read_1.fq.gz read_2.fq.gz > assembly.fna"""

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

    # Check executable dependencies
    spades = check_exec("spades.py")
    masurca = check_exec("masurca")
    samba = check_exec("samba.sh")

    if len(sys.argv) < 5 or len(sys.argv) > 6:
        print(__doc__, file=sys.stderr)
        return 1
    if sys.argv[1] not in {"masurca", "spades"}:
        print(__doc__, file=sys.stderr)
        return 1
    if sys.argv[2] not in {"denovo", "scaffold"}:
        print(__doc__, file=sys.stderr)
        return 1

    assembler = sys.argv[1]
    mode = sys.argv[2]
    nanopore = os.path.abspath(sys.argv[3])
    short = [os.path.abspath(file) for file in sys.argv[4:]]

    # Setup tmp directory
    tmp = Path(tempfile.mkdtemp(prefix=".tmp", dir=".")).resolve()
    atexit.register(shutil.rmtree, tmp)
    os.chdir(tmp)

    # Assembly stage
    if assembler == "masurca":
        cmd = [masurca, "-i", ",".join(short)]
        if mode == "denovo":
            cmd.extend(["-r", nanopore])
        iterator = map(
            str, Path(".").resolve().glob("CA*/primary.genome.scf.fasta")
        )
    else:
        cmd = [spades, "--careful", "-o", "."]
        if len(short) == 2:
            cmd.extend(["-1", short[0], "-2", short[1]])
        else:
            cmd.extend(["-s", short[0]])
        if mode == "denovo":
            cmd.extend(["--nanopore", nanopore])
        iterator = iter([os.path.abspath("scaffolds.fasta")])
    subprocess.run(cmd, check=True, stdout=sys.stderr)
    assembly = next(iterator)

    # Scaffolding stage (if asked)
    # See https://github.com/alekseyzimin/masurca?tab=readme-ov-file#samba-scaffolder
    min_match_length = 2000

    if mode == "scaffold":
        scaffold_tmp = Path(tempfile.mkdtemp(dir="."))
        os.chdir(scaffold_tmp)
        cmd = [
            samba, "-r", assembly, "-q", nanopore, "-m", str(min_match_length)
        ]
        subprocess.run(cmd, check=True, stdout=sys.stderr)
        assembly = os.path.abspath(f"{os.path.basename(assembly)}.scaffolds.fa")

    with open(assembly, encoding="utf8") as handle:
        shutil.copyfileobj(handle, sys.stdout)

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
