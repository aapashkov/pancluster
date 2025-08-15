#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: trim_nanopore.py FASTQ

Trim Oxford Nanopore reads from FASTQ file and print them to stdout.

example: trim_nanopore.py input.fastq.gz | gzip > output.fastq.gz"""

import atexit
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
    porechop = check_exec("porechop")
    fastp = check_exec("fastp")

    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 1

    file = Path(sys.argv[1])
    tmp = Path(tempfile.mkdtemp())
    atexit.register(shutil.rmtree, tmp)

    # Remove ONT adapters
    subprocess.run(
        [porechop, "-i", file, "-t", "1", "-o", tmp/"trimmed.fastq"],
        check=True,
        stdout=sys.stderr
    )

    # Remove reads shorter than 40bp
    subprocess.run(
        [
            fastp, "-i", tmp/"trimmed.fastq", "--stdout", "-A", "-Q",
            "-l", "40", "-j", tmp/"fastp.json", "-h", tmp/"fastp.html"
        ],
        check=True
    )

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
