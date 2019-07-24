# Flashfeed (Python version)

News feed for Alexa (and maybe friends).

## Build

```sh
docker build  -t flashfeed-python:latest .
```

## Start

```sh
docker run --name flashfeed-python -t flashfeed-python:latest
```

## Deploy

On the server, open port, if needed:

```sh
ufw allow 41384/tcp
```
