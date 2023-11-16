# Mexican Fusarium

### Preparation

1. Clone this repository.

```bash
git clone https://github.com/ccm-bioinfo/mexicanfusarium
cd mexicanfusarium
```

2. Create the conda environment from `env.yml` using your package manager of
choice (conda/mamba/micromamba) and activate it.

```bash
conda create -f env.yml
conda activate pancluster
```

3. Download and extract both Illumina and Nanopore data. You should have a file
structure like the following (some filenames are excluded or simplified).

<details><summary>Click to view file tree</summary>

```bash
.
├── NanoporeFusarium
│    └── 110823_tricho
│       └── 110823_Tricho
│           └── 110823_Tricho
│               └── 20230811_1436_MN33800_FAT01470_95dd06a8
│                   ├── fastq_fail
│                   │   ├── barcode07
│                   │   │   └── FAT01470_fail_barcode07_*.fastq.gz
│                   │   └── unclassified
│                   │       └── FAT01470_fail_unclassified_*.fastq.gz
│                   └── fastq_pass
│                       ├── barcode07
│                       │   └── FAT01470_pass_barcode07_*.fastq.gz
│                       └── unclassified
│                           └── FAT01470_pass_unclassified_*.fastq.gz
├── FASTQ_Generation_2019-10-19_02_18_21Z-194444306
│   ├── AH1FT1SS01_L001-ds.0e3d87a0edc141e7bd6615bf4de21d02
│   │   ├── AH1FT1SS01_S1_L001_R1_001.fastq.gz
│   │   └── AH1FT1SS01_S1_L001_R2_001.fastq.gz
│   ├── AH1FT1SS02_L001-ds.e84e63fd8ae04c12835852489bf22550
│   │   ├── AH1FT1SS02_S2_L001_R1_001.fastq.gz
│   │   └── AH1FT1SS02_S2_L001_R2_001.fastq.gz
│   └── AH1FT1SS03_L001-ds.20809b863fc148678b175c25afbc3b9c
│       ├── AH1FT1SS03_S3_L001_R1_001.fastq.gz
│       └── AH1FT1SS03_S3_L001_R2_001.fastq.gz
└── illumina.fa    # Illumina-only assembly
```

</details>

4. Concatenate Illumina and Nanopore reads for easier manipulation and remove
unnecessary files.

```bash
cat FASTQ*/*/*_R1_* > raw_illumina_1.fq.gz
cat FASTQ*/*/*_R2_* > raw_illumina_1.fq.gz
cat NanoporeFusarium/*/*/*/*/fastq_*/*/*.fastq.gz > raw_nanopore.fq.gz
rm -rf NanoporeFusarium
rm -rf FASTQ_Generation_2019-10-19_02_18_21Z-194444306
```

5. Download the antiSMASH databases into a directory of your choice. Here,
we'll download it into `adb/`

```bash
download-antismash-databases --database-dir adb/
```

File structure after preparation:

```bash
.
├── adb/                  # antiSMASH database
├── ids/                  # NCBI accessions and metadata
├── illumina.fa           # Illumina-only assembly
├── raw_illumina_1.fq.gz  # Illumina forward reads
├── raw_illumina_2.fq.gz  # Illumina reverse reads
└── raw_nanopore.fq.gz    # Nanopore reads
```

### Pipeline

The entire pipeline is contained within the `commands.sh` script. It
automatically skips already finished steps. General information is printed to
stderr, whereas program-specific logs are saved into `out/log.txt`.

```text
Usage: commands.sh -i illumina -1 f1 -2 f2 -n nanopore -o out

options:
  -i illumina   Illumina-only assembly file
  -1 f1         Illumina forward reads file
  -2 f2         Illumina reverse reads file
  -n nanopore   Nanopore reads file
  -d adb        antiSMASH database directory
  -o out        output directory
  -p proc       maximum number of CPUs to use (default: all available)
```

Run the script using the files from the preparation step.

```bash
./commands.sh -i illumina.fa -1 raw_illumina_1.fq.gz -2 raw_illumina_2.fq.gz \
  -n raw_nanopore.fq.gz -d adb/ -o outputs/
```

The output directory should have the following structure (some filenames are
deliberately excluded or simplified):

```bash
outputs/
├── alignment/
│   ├── alignment.sam  # BWA mem output
│   ├── reference.fa -> outputs/genomes/fna/GCF_013085055.1.fna
│   └── reference.fa.{amb,ann,bwt,pac,sa}  # BWA index outputs
├── assembly/
│   ├── masurca/  # MaSuRCA outputs
│   ├── hybrid.fa -> outputs/assembly/masurca/*/primary.genome.scf.fasta
│   └── stats.tsv  # BBtools statswrapper.sh table
├── bgc/  # antiSMASH results
│   ├── GCF_*/
│   └── hybrid/
├── genomes/  # Reference genomes
│   ├── fna/
│   │   └── GCF_*
│   ├── gff/
│   │   └── GCF_*
│   └── gff_filtered/
│       └── GCF_*
├── reads/  # Trimmed reads
│   ├── illumina_1.fq.gz
│   ├── illumina_2.fq.gz
│   └── nanopore.fq.gz
└── log.txt
```
