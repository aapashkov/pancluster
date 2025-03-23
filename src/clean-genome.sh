#!/bin/bash
{
set -euo pipefail
IFS=$'\t\n'

help="usage: $(basename "$0") INFILE OUTFILE

Mask repetitive sequences and remove comments from headers of INFILE fasta and
save results in OUTFILE.

example $(basename "$0") input.fasta output.fasta"

# Show help message if insufficient parameters
[[ "$#" -lt 2 ]] && printf '%s\n' "$help" && exit 1

# Setup variables, inputs, outputs and temporary directory
infile=$1
outfile=$2
tmp=$(mktemp -p "$(dirname "$outfile")" .tmp.XXX)
printf '%s\n' "created temporary file '$tmp'"
trap 'rm -vf "$tmp" >&2' EXIT

# Check that output file does not exist
[[ -e "$outfile" ]] && \
  printf '%s\n' "error: output '$outfile' already exists, not overwriting" && \
  exit 1

# Check for required programs
for program in seqtk tantan; do
  if ! command -v "$program" > /dev/null; then
    printf '%s\n' "error: $program: command not found"
    exit 1
  fi
done

# Mask repetitive sequences and remove comments from headers
tantan "$infile" | seqtk seq -Cl 80 > "$tmp"
chmod -v 666 "$tmp"
mv -v "$tmp" "$outfile"

exit 0
} >&2
