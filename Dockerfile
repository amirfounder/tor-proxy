FROM python:3.10-slim-buster

RUN \
    apt update && \
    apt upgrade && \
    apt install -y tor curl && \
    echo "SocksPort 0.0.0.0:9050" >> /etc/tor/torrc && \
    echo "ControlPort 9051" >> /etc/tor/torrc && \
    echo "CookieAuthentication 1" >> /etc/tor/torrc


COPY . ./app

WORKDIR /app

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD python main.py
