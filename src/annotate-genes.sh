#!/bin/bash
{
set -euo pipefail
IFS=$'\t\n'

help="usage: $(basename "$0") SPECIES INFILE OUTFILE

Annotate genes in INFILE using pretrained parameters of SPECIES and save results
as gff in OUTFILE.

example: $(basename "$0") fusarium_graminearum genome.fasta annotations.gff"

# Show help message if insufficient parameters
[[ "$#" -lt 3 ]] && printf '%s\n' "$help" && exit 1

# Setup variables, inputs, outputs and temporary file
species=$1
infile=$2
outfile=$3
outdir=$(dirname "$outfile")
tmp=$(mktemp -p "$outdir" .tmp.XXX)
printf '%s\n' "created temporary file '$tmp'"
trap 'rm -vf "$tmp" >&2' EXIT

# Check for required programs
if ! command -v augustus > /dev/null; then
  printf '%s\n' "error: augustus: command not found"
  exit 1
fi

augustus --species="$species" --gff3=on "$infile" | grep -v '^#' > "$tmp"
chmod -v 666 "$tmp"
mv -v "$tmp" "$outfile"

exit 0
} >&2
