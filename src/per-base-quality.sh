#!/bin/bash
{
# Set Bash strict mode
set -euo pipefail
IFS=$'\t\n'

help="usage: $(basename "$0") READ OUTFILE

Create per-base quality box plot from READ file and save it as a png file to
OUTFILE.

example: $(basename "$0") reads.fastq.gz result.png"

# Show help message if insufficient parameters
[[ "$#" -lt 1 ]] && printf '%s\n' "$help" && exit 1

# Check for required programs
for program in fastqc unzip; do
  if ! command -v $program > /dev/null; then
    printf '%s\n' "error: $program: command not found"
    exit 1
  fi
done

# Setup variables, inputs, outputs and temporary directory
CPUS=${CPUS:-1}
infile=$1
outfile=$2
outdir=$(dirname "$outfile")
outbase=$(basename "$outfile")
tmp=$(mktemp -dp "$outdir" .tmp.XXX)
printf '%s\n' "created temporary directory '$tmp'"
trap 'rm -vrf "$tmp" >&2' EXIT

fastqc --threads "$CPUS" --outdir "$tmp" "$infile"
tmpbase=$(basename -as .zip "$tmp"/*.zip)
unzip -p "$tmp/$tmpbase.zip" "$tmpbase/Images/per_base_quality.png" \
  > "$tmp/${outbase}"

chmod -v 666 "$tmp/${outbase}"
mv -v "$tmp/${outbase}" "$outfile"

exit 0
} >&2
