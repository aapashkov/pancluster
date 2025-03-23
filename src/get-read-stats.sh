#!/bin/bash
{
# Set Bash strict mode
set -euo pipefail
IFS=$'\t\n'

help="usage: $(basename "$0") INFILE OUTFILE

Extract statistics from reads in INFILE and save them as tsv in OUTFILE.

example: $(basename "$0") reads.fastq.gz stats.tsv"

# Show help message if insufficient parameters
[[ "$#" -lt 2 ]] && printf '%s\n' "$help" && exit 1

# Check for required programs
if ! command -v NanoStat > /dev/null; then
  printf '%s\n' "error: NanoStat: command not found"
  exit 1
fi

# Setup variables, inputs, outputs and temporary directory
CPUS=${CPUS:-1}
infile=$1
outfile=$2
outdir=$(dirname "$outfile")
outbase=$(basename "$outfile")
tmp=$(mktemp -dp "$outdir" .tmp.XXX)
printf '%s\n' "created temporary directory '$tmp'"
trap 'rm -vrf "$tmp" >&2' EXIT

# Calculate statistics
NanoStat --fastq "$infile" --tsv --threads "$CPUS" > "$tmp/$outbase"
chmod -v 666 "$tmp/$outbase"
mv -v "$tmp/$outbase" "$outfile"

exit 0
} >&2
