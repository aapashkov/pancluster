ARG DEBIAN_FRONTEND=noninteractive

# Install dependencies that can only be installed through micromamba while
# ignoring subdependencies as those will be satisfied in the second stage.
FROM mambaorg/micromamba:2.0.8-ubuntu24.04 AS micromamba

COPY env/*.yml /tmp

RUN micromamba install --name base --yes --no-deps --file /tmp/base.yml && \
    micromamba create --yes --no-deps --file /tmp/masurca.yml && \
    micromamba clean --all --yes && \
    rm -rf /opt/conda/pkgs \
        /opt/conda/conda-meta \
        /opt/conda/envs/masurca/conda-meta

# Copy dependencies from the micromamba stage and download the rest of them with
# apt and pip. Minor fixes are introduced to solve dependency issues.
FROM ubuntu:noble

# Environment variables needed by Funannotate
ENV PASAHOME=/usr/opt/pasa-2.5.3 \
    TRINITYHOME=/usr/lib/trinityrnaseq \
    EVM_HOME=/usr/opt/evidencemodeler-2.1.0 \
    AUGUSTUS_CONFIG_PATH=/usr/share/augustus/config \
    FUNANNOTATE_DB=/ext/data/databases/funannotateDB \
    QUARRY_PATH=/usr/opt/codingquarry-2.0/QuarryFiles

COPY --from=micromamba /opt/conda /usr
COPY env/*.txt /tmp

# Copy executables not provided by apt
COPY env/cmd/ete3 /usr/bin/ete3
COPY env/cmd/trimmomatic /usr/share/java/trimmomatic

RUN apt update && \
    xargs -a /tmp/apt.txt apt install --no-install-recommends --yes && \
    # Python and dependency requirements will be guaranteed
    pip install --break-system-packages \
        --no-cache-dir \
        --ignore-requires-python \
        --no-deps \
        --requirement /tmp/pip.txt && \
    apt clean && \
    rm /tmp/*.txt && \
    # Remove unused but problematic import in Funannotate library
    sed -i '/module_for_loader$/ s/^/# /' \
        /usr/local/lib/python3.12/dist-packages/funannotate/library.py && \
    # Force use latin encoding when checking Funannotate dependencies
    sed -i '/import fun/a\import functools as ft\nsubprocess.Popen = ft.partial(subprocess.Popen, encoding="latin-1")' \
        /usr/local/lib/python3.12/dist-packages/funannotate/check.py && \
    # Symlink executables so other programs can find them
    ln -sf fasta36 /usr/bin/fasta && \
    ln -s ../envs/masurca/bin/masurca /usr/bin/masurca && \
    ln -s snap-hmm /usr/bin/snap && \
    ln -s ../share/java/trimmomatic /usr/bin/trimmomatic && \
    chmod a+x /usr/bin/ete3 /usr/share/java/trimmomatic

WORKDIR /ext
