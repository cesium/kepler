FROM debian:trixie
EXPOSE 8000

WORKDIR /opt
COPY kepler/ /opt/kepler/
COPY pyproject.toml setup.py /opt/

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update  -y                                                         && \
    apt upgrade -y                                                         && \
    apt install -y --no-install-recommends python3 python3-venv coinor-cbc && \
    apt clean                                                              && \
    python3 -m venv .venv                                                  && \
    . .venv/bin/activate                                                   && \
    pip install .

ENTRYPOINT . .venv/bin/activate && python -m kepler api 0.0.0.0 8000
