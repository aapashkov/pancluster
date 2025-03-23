#!/bin/bash
{
# Set Bash strict mode
set -euo pipefail
IFS=$'\t\n'

# Prints help message
show_help() {
  echo "Usage: $0 [-l READS] [-1 READS] [-2 READS]" >&2
  echo "Perform genome assembly of READS and print it to stdout." >&2
  echo "" >&2
  echo "Options:" >&2
  echo "  -l READS        file with long reads (eg. Oxford Nanopore)" >&2
  echo "  -1 READS        file with short reads (eg. Illumina)" >&2
  echo "  -2 READS        file with paired-end reads (requires -1)" >&2
  echo "" >&2
  echo "Examples:" >&2 
  echo "  $0 -1 short.fq.gz > assembly.fna" >&2
  echo "  $0 -l long.fq.gz > draft.fna" >&2
  echo "  $0 -l long.fq.gz -1 short_1.fq.gz -2 short_2.fq.gz > hybrid.fna" >&2
}

# Show help message if insufficient parameters
if [[ "$#" -lt 2 ]]; then
  show_help
  exit 1
fi

# Parse parameters
while getopts ":l:1:2:" opt; do
  case $opt in
    l)  long="$OPTARG" ;;
    1)  short1="$OPTARG" ;;
    2)  short2="$OPTARG" ;;
    \?) echo "Error: invalid option: -$OPTARG" >&2 && exit 1 ;;
    :)  echo "Error: option -$OPTARG requires an argument" >&2 && exit 1 ;;
  esac
done

# Check parameters
[[ -z "${long+x}" && -z "${short1+x}" ]] && \
  echo "Error: one of the following arguments is required: -l, -1" >&2 && \
  exit 1
[[ -n "${short2+x}" && -z "${short1+x}" ]] && \
  echo "Error: when passing -2, an argument to -1 must be passed too" >&2 && \
  exit 1

# Check for required programs
if ! command -v masurca > /dev/null; then
  echo "Error: masurca: command not found" >&2
  exit 1
fi

# Setup variables, inputs, outputs and temporary directory
CPUS=${CPUS:-$(nproc)} # Use all processors if CPUS variable is not set
params=(-t "$CPUS")
[[ -n "${long+x}" ]] && params+=(-r "$(readlink -f "$long")")
if [[ -n "${short2+x}" ]]; then
  params+=(-i "$(readlink -f "$short1"),$(readlink -f "$short1")")
elif [[ -n "${short1+x}" ]]; then
  params+=(-i "$(readlink -f "$short1")")
fi
[[ -n "${reference+x}" ]] && reference="$(readlink -f "$reference")"
tmp=$(mktemp -d)
echo "created temporary directory '$tmp'" >&2
# trap 'rm -vrf "$tmp" >&2' EXIT

# Run assembly
cd "$tmp"
masurca "${params[@]}"
cat CA.*/primary.genome.scf.fasta

exit 0
}
