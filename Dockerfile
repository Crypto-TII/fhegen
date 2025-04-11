FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    m4 \
    python3-dev \
    sagemath \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN sage -python3 -m pip install prettytable scipy sphinx==5.3.0 furo pytest pytest-cov

WORKDIR /home/fhegen/

COPY . .