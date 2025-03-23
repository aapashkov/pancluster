#!/bin/bash
{
set -euo pipefail
IFS=$'\t\n'

help="usage: $(basename "$0") TAXON FASTA GFF OUTDIR [PATHDB]

Annotate BGCs in genome of a TAXON (bacteria or fungi) stored in FASTA file with
its corresponding annotations stored in GFF, and save results to OUTDIR. When
specified, use PATHDB as path to antiSMASH database instead of the default one.
The basename of OUTDIR is used as organism name in output gbk files.

example: $(basename "$0") fungi genome.fna annotations.gff outputs/"

# Show help message if insufficient parameters
[[ "$#" -lt 4 ]] && printf '%s\n' "$help" && exit 1

# Setup variables, inputs, outputs and temporary directory
CPUS=${CPUS:-1}
taxon=$1
fasta=$2
gff=$3
outdir=$4
outbase="$(basename "$outdir")"
tmp=$(mktemp -dp "$(dirname "$outdir")" .tmp.XXX)
printf '%s\n' "created temporary directory '$tmp'"
trap 'rm -rvf "$tmp" >&2' EXIT

# Check that output directory does not exist
[[ -e "$outdir" ]] && \
  printf '%s\n' "error: output '$outdir' already exists, not overwriting" && \
  exit 1

# Check for required programs
if ! command -v antismash > /dev/null; then
  printf '%s\n' "error: antismash: command not found"
  exit 1
fi

# If no PATHDB supplied, run antismash with default database
if [[ -z "${5+x}" ]]; then
  databases=""
else
  databases="--databases $5"
fi

# shellcheck disable=SC2086
antismash --cpus "$CPUS" $databases \
  --taxon "$taxon" \
  --cb-knownclusters \
  --output-dir "$tmp/$outbase" \
  --output-basename "$outbase" \
  --genefinding-tool none \
  --genefinding-gff3 "$gff" \
  "$fasta"

# Add output basename to ORGANISM in gbks, and move results out of tmp directory
sed -i 's/^  ORGANISM.*/  ORGANISM  '"$outbase"'/' "$tmp/$outbase"/*.gbk
find "$tmp/$outbase" -type d -exec chmod 777 {} +
find "$tmp/$outbase" -type f -exec chmod 666 {} +
mv -v "$tmp/$outbase" "$outdir"

exit 0
} >&2
