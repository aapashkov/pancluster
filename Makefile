SHELL := bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += -j$(shell nproc)

ifeq ($(origin .RECIPEPREFIX), undefined)
  $(error This Make does not support .RECIPEPREFIX. Please use GNU Make 4.0 or later)
endif
.RECIPEPREFIX = >

# Function that logs a message with current datetime
log = date '+[%F %T]: $(1)' >&2

# Variables
markers = its tub
reads = SRR32310738 SRR32193854 SRR32310737 SRR32193853
col = :

all: $(markers:%=results/markers/%.svg) \
  $(reads:%=data/reads/raw/%_1.fastq.gz) \
  $(reads:%=data/reads/trimmed/%_1.fastq.gz)
> @$(call log,All finished)

run:
> @docker run --rm -itv .$(col)/ext -u $(shell id -u)$(col)$(shell id -g) \
  --env-file .env --name pancluster aapashkov/pancluster

root:
> @docker run --rm -itv .$(col)/ext --name pancluster aapashkov/pancluster

# Phylogenetic tree reconstruction
results/markers/%.svg:
> @$(call log,Building phylogenetic tree for $*) && \
  mkdir -p results/markers && \
  python3 scripts/phylogenetic_tree.py data/markers/$*.fasta > $@ \
    2> logs/tree_$*.log && \
  $(call log,Finished building phylogenetic tree for $*)

# Raw read downloading
data/reads/raw/%_1.fastq.gz:
> @$(call log,Downloading $*) && \
  mkdir -p data/reads/raw && \
  python3 scripts/download_reads.py $* data/reads/raw 2> /dev/null && \
  $(call log,Finished downloading $*)

# Read trimming
data/reads/trimmed/%_1.fastq.gz: data/reads/raw/%_1.fastq.gz
> @$(call log,Trimming $*) && \
  mkdir -p data/reads/trimmed && \
  if [[ -f data/reads/raw/$*_2.fastq.gz ]]; then \
    python3 scripts/trim_illumina.py $< data/reads/raw/$*_2.fastq.gz \
      data/reads/trimmed/$* 2> logs/trim_$*.log; \
  else \
    python3 scripts/trim_nanopore.py $< 2> logs/trim_$*.log | gzip > $@; \
  fi; \
  $(call log,Finished trimming $*)
