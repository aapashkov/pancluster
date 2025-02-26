#!/bin/bash
{
# Set Bash strict mode
set -euo pipefail
IFS=$'\t\n'

help="usage: $(basename "$0") INFILE OUTFILE

Trim Nanopore reads from INFILE and save them gzip-compressed in OUTFILE.

example: $(basename "$0") raw.fastq.gz trimmed.fastq.gz"

# Show help message if insufficient parameters
[[ "$#" -lt 2 ]] && printf '%s\n' "$help" && exit 1

# Check for required programs
for program in porechop fastp; do
  if ! command -v $program > /dev/null; then
    printf '%s\n' "error: $program: command not found"
    exit 1
  fi
done

if ! command -v gzip > /dev/null && ! command -v pigz > /dev/null; then
  printf '%s\n' "error: gzip or pigz required but neither is available"
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

# Set gzip compressor to pigz if available
compress() {
  if command -v pigz > /dev/null; then
    pigz -vp "$CPUS" < "$1"
  else
    gzip -v < "$1"
  fi
}

# Remove adapters and short reads
porechop --input "$infile" \
  --threads "$CPUS" | \
fastp --stdin \
  --stdout \
  --disable_adapter_trimming \
  --disable_quality_filtering \
  --length_required 40 \
  --json "$tmp/fastp.json" \
  --html "$tmp/fastp.html" \
  --thread "$CPUS" | \
compress /dev/stdin > "$tmp/${outbase}"

chmod -v 666 "$tmp/${outbase}"
mv -v "$tmp/${outbase}" "$outfile"

exit 0
} >&2
