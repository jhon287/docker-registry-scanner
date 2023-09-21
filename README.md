# Docker Registry Scanner

## Description

The goal of this application is to scan Docker images stored on a [registry](https://github.com/docker) (for now only registry made by [Docker Inc.](https://github.com/docker)).

Scan is done using Trivy security scanner.

Docker Registry Scanner application writes status of images as standard output and scan results report JSON file (defaults: `./scan_results_report.json`) is created at the end of the run.

**Example**

```shell
Scanning Docker image 'localhost:443/my-poc:latest'...
🔴 NOK  localhost:443/my-poc:latest ({'HIGH': 1, 'CRITICAL': 0})
Scanning Docker image 'localhost:443/semver-bumper:08dc6233'...
Scanning Docker image 'localhost:443/semver-bumper:latest'...
🔴 NOK  localhost:443/semver-bumper:08dc6233 ({'HIGH': 1, 'CRITICAL': 0})
🟢 OK   localhost:443/semver-bumper:latest
Scanning Docker image 'localhost:443/ubuntu:latest'...
🟢 OK   localhost:443/ubuntu:latest
```

## Configuration

### Environment Variables

- `LOGGING_LEVEL`: (Optional) Logging level needed. Can be `DEBUG`, `INFO`, `WARNING` or `CRITICAL`. (Default: `INFO`)
- `DOCKER_REGISTRY_URL`: **(Required)** Docker registry **HTTPS** URL that needs to be scanned. (e.g. `https://docker-registry.example.com:12345/path/to/repository/`)
- `DOCKER_REGISTRY_CA_FILE`: (Optional) PEM format file of CA.
- `DOCKER_IMAGES_FILTER`: (Optional) REGEX pattern used to filter Docker images. (Default: `.*`)
- `DOCKER_TAGS_FILTER`: (Optional) REGEX pattern used to filter Docker image tags. (Default: `.*`)
- `IMAGE_LIST_NBR_MAX`: (Optional) Maximum number of Docker images that needs to be fetch from Docker registry. (Default: `1000`)
- `HTTPS_CONNECTION_TIMEOUT`: (Optional) Docker registry client HTTPS connection timeout. (Default: `3`)
- `SCAN_SEVERITY`: (DEPRECATED) Scanner severity configuration. Deprecated in favor of `SCAN_MIN_SEVERITY`. (Default: `HIGH,CRITICAL`)
- `SCAN_MIN_SEVERITY`: (Optional) Scanner minimum severity threshold. Can be `UNKNOWN`, `LOW`, `MEDIUM`, `HIGH` or `CRITICAL`. (Defaut: `HIGH`)
- `SCAN_RESULTS_REPORT_FILE`: (Optional) Scanner results report file. (Default: `./scan_results_report.json`)
- `SCAN_SCANNERS`: (Optional) Scanner scan types to do. (Default: `vuln,secret`)
- `MULTIPROCESSING_PROCESSES`: (Optional): Process in parallel used to scan Docker images. (Default: `5`)


## Docker

### Build

```shell
docker build -t docker-registry-scanner .
```

### Run

**Examples**

```shell
# Minimum required
docker run \
    --rm \
    -e DOCKER_REGISTRY_URL="https://docker-registry.example.com:12345" \
    docker-registry-scanner

# Filter Docker images, minimum scan severity 'LOW' and logging level 'DEBUG'
docker run \
    --rm \
    -e DOCKER_REGISTRY_URL="https://docker-registry.example.com:12345" \
    -e DOCKER_IMAGES_FILTER='^release/docker/internal/speos/$' \
    -e SCAN_MIN_SEVERITY="LOW" \
    -e LOGGING_LEVEL="DEBUG" \
    docker-registry-scanner

# HTTPS Proxy to reach Trivy databases URLs
docker run \
    --rm \
    -e DOCKER_REGISTRY_URL="https://docker-registry.example.com:12345" \
    -e https_proxy="http://proxy.example.com:7890" \
    docker-registry-scanner
```
