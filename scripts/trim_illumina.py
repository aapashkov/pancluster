#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: trim_illumina.py READ [READ2] OUTPREFIX

Trim Illumina READ file, with optional paired end READ2 file, and save results
to OUTPREFIX.

example: trim_illumina.py raw_1.fq.gz raw_2.fq.gz trimmed"""

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
    trim = check_exec("trim_galore")

    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print(__doc__, file=sys.stderr)
        return 1

    files = list(map(
        Path, sys.argv[1:3] if len(sys.argv) == 4 else sys.argv[1:2]
    ))
    out = Path(sys.argv[-1])
    tmp = Path(tempfile.mkdtemp())
    atexit.register(shutil.rmtree, tmp)

    # Run Illumina trimming
    cmd = [
        trim, "--illumina", "--length", "40", "-o", tmp, "--no_report_file",
        "--basename", out.name, "-j", "1", "--gzip"
    ]
    if len(files) == 2:
        cmd.append("--paired")
    cmd.extend(files)
    subprocess.run(cmd, check=True, stdout=sys.stderr)

    # Move output to final destination
    if len(files) == 2:
        shutil.move(tmp/f"{out.name}_val_1.fq.gz", f"{out}_1.fastq.gz")
        shutil.move(tmp/f"{out.name}_val_2.fq.gz", f"{out}_2.fastq.gz")
    else:
        shutil.move(tmp/f"{out.name}_trimmed.fq.gz", f"{out}.fastq.gz")

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
