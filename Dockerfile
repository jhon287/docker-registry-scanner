ARG PYTHON_VERSION="3.11"

FROM debian:12-slim AS gpg-dearmor

COPY pubkeys/trivy.key /tmp

# DL3008 warning: Pin versions in apt get install
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install --no-install-recommends -y gnupg \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && gpg --dearmor > /tmp/trivy.gpg < /tmp/trivy.key

FROM python:"${PYTHON_VERSION}-slim"

LABEL org.opencontainers.image.authors="Jonathan Sabbe <sabbe.jonathan@gmail.com>"

WORKDIR /app

COPY src/ .
COPY apt/trivy.sources /etc/apt/sources.list.d/
COPY --from=gpg-dearmor /tmp/trivy.gpg /etc/apt/trusted.gpg.d/trivy.gpg

ARG TRIVY_VERSION="0.45.1"

# DL3008 warning: Pin versions in apt get install
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install --no-install-recommends -y git trivy=$TRIVY_VERSION \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && adduser --disabled-password --comment "Docker Scanner" scanner \
    && chown -R scanner:scanner . \
    && pip uninstall -y setuptools

USER scanner

RUN git config --global --add safe.directory "${PWD}"

ENV TZ="Europe/Brussels" \
    PYTHONUNBUFFERED="1"

ENTRYPOINT [ "python", "main.py" ]
