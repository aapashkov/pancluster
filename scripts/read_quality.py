#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: read_quality.py FASTQ

Print a table in TSV format to stdout showing length and quality statistics of a
FASTQ file.

example: read_quality.py input.fastq.gz > stats.tsv"""

import re
import shutil
import subprocess
import sys
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
    nanostat = check_exec("NanoStat")

    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 1

    file = Path(sys.argv[1])
    subprocess.run([nanostat, "--tsv", "--fastq", file], check=True)

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
