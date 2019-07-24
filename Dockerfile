FROM python:3.7.4-alpine3.10
LABEL maintainer="Alessandro Iob <alessandro.iob@gmail.com>"

RUN apk add tzdata && ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime

# Environment setting
ENV APP_ENVIRONMENT production

# Python application
RUN mkdir -p /srv/flashfeed
WORKDIR /srv/flashfeed
COPY ./requirements.txt .
RUN pip install -r ./requirements.txt
COPY ./flashfeed ./flashfeed
COPY ./config ./config

EXPOSE 41384

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:41384", "flashfeed.__main__:server"]
