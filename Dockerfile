FROM python:latest
LABEL maintainer="Alessandro Iob <alessandro.iob@gmail.com>"

# Environment setting
ENV APP_ENVIRONMENT production

# Python application
RUN mkdir -p /srv/flashfeed
WORKDIR /srv/flashfeed
COPY ./requirements.txt .
RUN pip install -r ./requirements.txt
COPY ./flashfeed ./flashfeed
COPY ./config ./config

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "flashfeed.__main__:server"]
