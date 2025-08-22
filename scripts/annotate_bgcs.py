#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: annotate_bgcs.py GBK OUTDIR

Annotate a fungal GBK and save results to OUTDIR. Set ANTISMASHDB environment
variable to your antiSMASH database location.

example: annotate_bgcs.py input.gbk output/"""

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

    antismash = check_exec("antismash")
    db = os.environ.get("ANTISMASHDB", "/ext/data/databases/antismashDB")

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

    # Run antiSMASH
    subprocess.run(
        [
            antismash, "--cpus", "10", "--taxon", "fungi",
            "--output-dir", file.stem, "--output-basename", file.stem,
            "--html-title", file.stem, "--databases", db,
            "--allow-long-headers", "--genefinding-tool", "none", file
        ],
        check=True
    )

    # Move result out of tmp directory
    shutil.move(file.stem, outdir/file.stem)

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
