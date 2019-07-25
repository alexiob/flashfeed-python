# Flashfeed (Python version)

News feed for Alexa (and maybe friends).

## Local Build

```sh
docker build -t flashfeed-python:latest .
```

## Local Start

Python:

```sh
gunicorn --bind 0.0.0.0:41384 "flashfeed.__main__:server"
```

Docker:

```sh
docker stop flashfeed-python
docker run --name flashfeed-python --rm -p 41384:41384 -t flashfeed-python:latest
```

## Start

```sh
docker stop flashfeed-python
docker run \
 -v /etc/letsencrypt/live/flashfeed.iob.toys/fullchain.pem:/ssl/fullchain.pem \
 -v /etc/letsencrypt/live/flashfeed.iob.toys/privkey.pem:/ssl/privkey.pem\
 --name flashfeed-python --rm -d -p 443:41384 -t \
 alexiob/flashfeed-python:latest
```

## Deploy

On the Ubuntu server, open the `443` port, if needed:

```sh
ufw allow 443/tcp
```

## Endpoint Test

```sh
curl -X GET https://flashfeed.iob.toys/v1/api/alexa/flashfeed/rainews/fvg/gr
```
