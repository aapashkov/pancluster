#!/bin/bash
{
# Set Bash strict mode
set -euo pipefail
IFS=$'\t\n'

help="usage: $(basename "$0") OUTDIR ACCESSION

Download reads of an ACCESSION from the Sequence Read Archive and save them
gzip-compressed in OUTDIR.

example: $(basename "$0") ./output/reads SRR32193854"

# Show help message if insufficient parameters
[[ "$#" -lt 2 ]] && printf '%s\n' "$help" >&2 && exit 1

# Setup variables, inputs, outputs and temporary directory
CPUS=${CPUS:-1}
outdir=$1
accession=$2
tmp=$(mktemp -dp "$outdir" .tmp.XXX)
printf '%s\n' "created temporary directory '$tmp'" >&2
trap 'rm -vrf "$tmp" >&2' EXIT

# Check for required programs
if ! command -v fasterq-dump > /dev/null; then
  printf '%s\n' "error: fasterq-dump: command not found" >&2
  exit 1
fi

if ! command -v gzip > /dev/null && ! command -v pigz > /dev/null; then
  printf '%s\n' "error: gzip or pigz required but neither is available" >&2
  exit 1
fi

# Download files
prefetch --output-directory "$tmp" --progress "$accession"
# shellcheck disable=SC2016
fasterq-dump --outdir "$tmp" \
  --temp "$tmp" \
  --threads "$(nproc)" \
  --progress \
  --details \
  --seq-defline '@$ac.$si/$ri' \
  --qual-defline '+' \
  "$tmp/$accession" >&2
rm -v "$tmp/$accession"/*
rmdir -v "$tmp/$accession"

# Compress outputs
if command -v pigz > /dev/null; then
  pigz -vp "$CPUS" "$tmp"/* >&2
else
  gzip -v "$tmp"/* >&2
fi
chmod -v 666 "$tmp"/* >&2
mv -v "$tmp"/* "$outdir"/ >&2

exit 0
}
