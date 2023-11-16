FROM mambaorg/micromamba:1.5.1

COPY --chown=$MAMBA_USER:$MAMBA_USER env.yml /tmp/env.yml

# System requirements
USER root
RUN apt update -yqq && \
    apt install -yqq build-essential wget cmake zlib1g-dev libbz2-dev git && \
    rm -rf /var/lib/apt/lists/* /var/log/dpkg.log

USER $MAMBA_USER
RUN micromamba install -yqn base -f /tmp/env.yml && \
    micromamba clean -yqa && \
    rm /tmp/env.yml

# SPAdes
RUN cd && \
    mkdir spades && \
    wget http://cab.spbu.ru/files/release3.15.5/SPAdes-3.15.5.tar.gz && \
    tar -xzf SPAdes-3.15.5.tar.gz && \
    cd SPAdes-3.15.5 && \
    PREFIX=/home/mambauser/spades ./spades_compile.sh && \
    cd && \
    cp -r spades/* /opt/conda/. && \
    rm -rf spades/ SPAdes-3.15.5*

WORKDIR /tmp
