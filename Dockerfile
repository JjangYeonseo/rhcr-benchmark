FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libboost-program-options-dev \
    libboost-system-dev \
    libboost-filesystem-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/rhcr

COPY . .

RUN cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build --parallel 2
