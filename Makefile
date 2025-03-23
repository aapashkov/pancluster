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

# Variable definitions
basedirs = data results data/logs
paired_illumina = SRR32310738 SRR32193854
nanopore = SRR32310737 SRR32193853
logs = data/logs
reads = data/reads
raw = data/reads/raw
trimmed = data/reads/trimmed
qualities = results/qualities
read_stats = results/read-stats

all: $(paired_illumina:%=$(raw)/%_1.fastq.gz) \
  $(nanopore:%=$(raw)/%.fastq.gz) \
  $(paired_illumina:%=$(trimmed)/%_1.fastq.gz) \
  $(nanopore:%=$(trimmed)/%.fastq.gz) \
  $(paired_illumina:%=$(qualities)/%.png) \
  $(nanopore:%=$(read_stats)/%.tsv) \
  $(paired_illumina:%=$(read_stats)/%.tsv)
> @$(call log,All finished)

# Downloads reads from SRA
$(raw)/%.fastq.gz:
> @$(eval accession := $(patsubst %_1,%,$*))
> @$(call log,Downloading $(accession)) && \
  mkdir -pm 777 $(basedirs) $(reads) $(raw) && \
  $(SHELL) ./src/download-reads.sh $(raw) $(accession) \
    &> $(logs)/download-$(accession).log && \
  chmod 666 $(logs)/download-$(accession).log && \
  $(call log,Finished downloading $(accession))

# Creates per-base quality plots from raw Illumina reads
$(qualities)/%.png: $(raw)/%_1.fastq.gz
> @$(call log,Checking quality of $*) && \
  mkdir -pm 777 $(basedirs) $(qualities) && \
  $(SHELL) ./src/per-base-quality.sh $< $@ &> $(logs)/quality-$*.log && \
  chmod 666 $(logs)/quality-$*.log && \
  $(call log,Finished checking quality of $*)

# Trims Illumina reads
$(trimmed)/%_1.fastq.gz: $(raw)/%_1.fastq.gz
> @$(call log,Trimming $*) && \
  mkdir -pm 777 $(basedirs) $(reads) $(trimmed) && \
  $(SHELL) ./src/trim-illumina.sh $(trimmed)/$* $(raw)/$*_1.fastq.gz \
    $(raw)/$*_2.fastq.gz &> $(logs)/trimming-$*.log && \
  chmod 666 $(logs)/trimming-$*.log && \
  $(call log,Finished trimming $*)

# Trims Nanopore reads
$(trimmed)/%.fastq.gz: $(raw)/%.fastq.gz
> @$(call log,Trimming $*) && \
  mkdir -pm 777 $(basedirs) $(reads) $(trimmed) && \
  $(SHELL) ./src/trim-nanopore.sh $< $@ &> $(logs)/trimming-$*.log && \
  chmod 666 $@ $(logs)/trimming-$*.log && \
  $(call log,Finished trimming $*)

# Extracts statistics from raw Illumina reads
$(read_stats)/%.tsv: $(raw)/%_1.fastq.gz
> @$(call log,Extracting statistics from $*) && \
  mkdir -pm 777 $(basedirs) $(read_stats) && \
  $(SHELL) ./src/get-read-stats.sh $< $@ &> $(logs)/stats-$*.log && \
  chmod 666 $@ $(logs)/stats-$*.log && \
  $(call log,Finished extracting statistics from $*)

# Extracts statistics from raw Nanopore reads
$(read_stats)/%.tsv: $(raw)/%.fastq.gz
> @$(call log,Extracting statistics from $*) && \
  mkdir -pm 777 $(basedirs) $(read_stats) && \
  $(SHELL) ./src/get-read-stats.sh $< $@ &> $(logs)/stats-$*.log && \
  chmod 666 $@ $(logs)/stats-$*.log && \
  $(call log,Finished extracting statistics from $*)
