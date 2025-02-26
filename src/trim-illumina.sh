#!/bin/bash
{
# Set Bash strict mode
set -euo pipefail
IFS=$'\t\n'

help="usage: $(basename "$0") OUTPREFIX READ [READ]

Trim Illumina READs and save them to OUTPREFIX. If two READs are provided, they
will be treated as paired-end files.

example: $(basename "$0") ./trimmed ./raw_1.fastq.gz ./raw_2.fastq.gz"

# Show help message if insufficient parameters
[[ "$#" -lt 2 ]] && printf '%s\n' "$help" && exit 1

# Check for required programs
if ! command -v trim_galore > /dev/null; then
  printf '%s\n' "error: trim_galore: command not found"
  exit 1
fi

# Setup variables, inputs, outputs and temporary directory
CPUS=${CPUS:-1}
outprefix=$1
file=$2
base=$(basename "$outprefix")
outdir=$(dirname "$outprefix")
tmp=$(mktemp -dp "$outdir" .tmp.XXX)
printf '%s\n' "created temporary directory '$tmp'"
trap 'rm -vrf "$tmp" >&2' EXIT

# If one READ is passed, perform single-end trimming
if [[ -z "${3+x}" ]]; then
  trim_galore --gzip \
    -o "$tmp" \
    --length 40 \
    --cores "$CPUS" \
    --illumina \
    --basename "$base" \
    --no_report_file \
    "$file"
  chmod -v 666 "${tmp}/${base}_trimmed.fq.gz"
  mv -v "${tmp}/${base}_trimmed.fq.gz" "${outprefix}.fastq.gz"

# If two READs were passed, run paired-end trimming
else
  file2=$3
  trim_galore --gzip \
    -o "$tmp" \
    --length 40 \
    --cores "$CPUS" \
    --illumina \
    --basename "$base" \
    --no_report_file \
    --paired \
    "$file" "$file2"
  chmod -v 666 "${tmp}/${base}_val_1.fq.gz" "${tmp}/${base}_val_2.fq.gz"
  mv -v "${tmp}/${base}_val_1.fq.gz" "${outprefix}_1.fastq.gz"
  mv -v "${tmp}/${base}_val_2.fq.gz" "${outprefix}_2.fastq.gz"
fi

exit 0
} >&2
