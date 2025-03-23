#!/usr/bin/env python3

"""Read gbk from stdin and extract translated proteins in fasta format to
stdout."""

import os
import sys

import Bio.SeqIO

def main() -> int:
    if sys.stdin.isatty():
        base = os.path.basename(__file__)
        help = "\n\n".join([
            f"usage: {base}", __doc__.replace("\n", " "),
            f"example: {base} < input.gbk > output.faa"
        ])
        print(help, file=sys.stderr)
        return 1
    for record in Bio.SeqIO.parse(sys.stdin, "genbank"):
        for feature in record.features:
            if feature.type == "CDS":
                print(f">{feature.qualifiers['gene'][0]}")
                print(f"{feature.qualifiers['translation'][0]}")
    return 0

if __name__ == "__main__":
    exit(main())
