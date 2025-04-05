FROM python:3-slim

# install deps
RUN apt-get update \
    && apt-get install -y iproute2 git dumb-init procps \
    && apt-get clean

# install deps
RUN pip install "fastapi[all]" jinja2

# clone ExaBGP
RUN git clone --single-branch --branch 4.2 https://github.com/Exa-Networks/exabgp /opt/exabgp

COPY app /opt/exabgp/app
COPY run.sh /opt/exabgp

RUN useradd -r exa \
    && mkdir /etc/exabgp \
    && mkfifo /run/exabgp.in \
    && mkfifo /run/exabgp.out \
    && chown exa /run/exabgp.in \
    && chown exa /run/exabgp.out \
    && chmod 600 /run/exabgp.in \
    && chmod 600 /run/exabgp.out

RUN echo "[exabgp.daemon]" > /opt/exabgp/etc/exabgp/exabgp.env \
    && echo "user = 'exa'" >> /opt/exabgp/etc/exabgp/exabgp.env

ENV PYTHONPATH=/opt/exabgp/src
ENV PATH=$PATH:/opt/exabgp/sbin/

ENTRYPOINT [ \
    "/usr/bin/dumb-init", "--", \ 
    "/opt/exabgp/sbin/exabgp" \
]
