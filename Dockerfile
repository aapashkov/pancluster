FROM ubuntu:20.04

# Build arguments
ARG DEBIAN_FRONTEND=noninteractive
ARG ARCH=64
ARG MICROMAMBA=2.3.1

# Environment definition files
COPY env/apt.txt /tmp/apt.txt
COPY env/pip.txt /tmp/pip.txt
COPY env/base.yml /tmp/base.yml

# Setup apt dependencies
RUN apt-get update && \
    xargs -a /tmp/apt.txt apt-get install --no-install-recommends --yes && \
    apt-get clean && \
    rm -rf /tmp/apt.txt /var/lib/apt /var/lib/dpkg /var/lib/cache /var/lib/log

# Setup conda dependencies
RUN wget -qO- "https://micro.mamba.pm/api/micromamba/linux-${ARCH}/${MICROMAMBA}" | tar -xjC "/" "bin/micromamba" && \
    mv /usr/local /tmp/local && \
    micromamba create --yes --prefix /usr/local --no-deps --file /tmp/base.yml && \
    micromamba clean --all --yes && \
    cp -r /tmp/local /usr && \
    rm -rf /tmp/base.yml /tmp/local

# Setup pip dependencies
RUN pip install --no-cache-dir --no-deps --requirement /tmp/pip.txt && \
    rm /tmp/pip.txt

# Copy missing CLI tools
COPY env/cmd/calcmem.sh /usr/share/bbmap/calcmem.sh

# Create symlinks to some programs so other tools can find them
RUN basename -a /usr/share/bbmap/*.sh | xargs -I {} ln -fs ../share/bbmap/{} /usr/bin/{} && \
    basename -as .sh /usr/share/bbmap/*.sh | xargs -I {} ln -fs {}.sh /usr/share/bbmap/{} && \
    # Create user's home directory
    mkdir /home/user && chmod 777 /home/user

WORKDIR /ext
