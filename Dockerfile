FROM alpine:3.22
EXPOSE 8000

WORKDIR /opt
COPY kepler/ /opt/kepler/
COPY pyproject.toml setup.py /opt/

RUN apk add --no-cache curl

RUN apk add --no-cache python3 && \
    python3 -m venv .venv      && \
    . .venv/bin/activate       && \
    pip install .


CMD ["/opt/.venv/bin/python", "-m", "kepler", "api", "0.0.0.0", "8000"]