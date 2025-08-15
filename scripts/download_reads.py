#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: download_reads.py ACCESSION [OUTDIR]

Download reads from SRA ACCESSION into OUTDIR if specified, or current directory
otherwise.

example: download_reads.py SRR32310737 reads/"""

import atexit
import csv
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.request import urlopen, urlretrieve


def progress(block_num: int, block_size: int, total_size: int):
    print(
        f"{block_num * block_size / total_size * 100:.2f}%",
        file=sys.stderr, end="\r"
    )


def main() -> int:
    """Driver code."""

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(__doc__, file=sys.stderr)
        return 1

    accession = sys.argv[1]
    out = Path(sys.argv[2] if len(sys.argv) == 3 else ".")
    tmp = Path(tempfile.mkdtemp())
    atexit.register(shutil.rmtree, tmp)

    # Retrieve list of read files of accession
    url = f"https://www.ebi.ac.uk/ena/portal/api/filereport?accession={accession}&result=read_run&fields=fastq_ftp"
    with urlopen(url) as handle:
        reader = csv.DictReader(map(bytes.decode, handle), delimiter="\t")
        raw_ftp = next(reader)["fastq_ftp"]
        ftps = [f"ftp://{link}" for link in raw_ftp.split(";")]

    # Download files into temporary directory
    for ftp in ftps:
        urlretrieve(ftp, tmp/Path(ftp).name, progress)

    # Move files to output directory
    for ftp in ftps:
        base = Path(ftp).name
        shutil.move(tmp/base, out/base)

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
