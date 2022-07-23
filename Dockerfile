FROM python:3-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt update && apt install -y git autoconf automake libtool make pkg-config

RUN git clone https://github.com/home-assistant-libs/pytradfri

RUN ./pytradfri/script/install-coap-client.sh

COPY . .

CMD python3 ./main.py -K $SECURITY_CODE $GATEWAY_IP