FROM mambaorg/micromamba:2.0.5-debian12-slim
USER root
COPY env.yml /tmp/env.yml
RUN micromamba install -yn base -f /tmp/env.yml && \
    micromamba clean -ay && \
    rm /tmp/env.yml
WORKDIR /ext
