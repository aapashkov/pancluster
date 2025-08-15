JOBS := $(shell nproc)
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += -j $(JOBS)

ifeq ($(origin .RECIPEPREFIX), undefined)
  $(error This Make does not support .RECIPEPREFIX. Please use GNU Make 4.0 or later)
endif
.RECIPEPREFIX = >

# Function that logs a message with current datetime
log = date '+[%F %T]: $(1)' >&2

# Variables
markers = its tub

all: $(markers:%=results/markers/%.svg)
> @$(call log,All finished)

results/markers/%.svg:
> @mkdir -p results/markers && \
  python3 scripts/phylogenetic_tree.py data/markers/$*.fasta > $@ \
    2> logs/$*.log && \
  $(call log,Finished building phylogenetic tree for $*)
