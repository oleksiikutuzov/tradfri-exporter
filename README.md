# tradfri-exporter
Export IKEA Tradfri devices battery status to Prometheus

## Run with Docker

You can run the image in the background with the following command:
```
docker run -d -p 8090:9090 --restart unless-stopped -e HOST_PORT=9090 -e UPDATE_INTERVAL=10.0 -e GATEWAY_IP=XXXXXX -e SECURITY_CODE=XXXXXX tradfri-exporter
```

To check image status:
```
docker ps -a
```

To stop running images:
```
docker stop tradfri-exporter
```

To start running the image:
```
docker start tradfri-exporter
```

To delete:
```
docker rm tradfri-exporter
```
## Run with Docker-compose

Create a `docker-compose.yml` file and add your configuration to it:

```
version: "3"

services:
  tradfri-exporter:
    container_name: tradfri-exporter
    image: oleksiikutuzov/tradfri-exporter:latest
    restart: always
    ports:
      - 8090:9090
    environment:
      HOST_PORT: 9090
      GATEWAY_IP: XXXXXX
      SECURITY_CODE: XXXXXX
      UPDATE_INTERVAL: 10.0
```

Then run the image with the following command:

```
docker-compose up -d
```
### To update the image:

```
docker pull oleksiikutuzov/tradfri-exporter
```

And use the `docker-compose` command again:

```
docker-compose up -d
```
## Manual installation

It is considered you already have python installed. Install required packages

```
pip3 install pytradfri
```
Then install `coap-client`
```
git clone https://github.com/home-assistant-libs/pytradfri
sudo ./pytradfri/script/install-coap-client.sh
```
## Run with systemd

Almost all versions of Linux come with systemd out of the box, but if your’s didn’t come with it then you can simply run the following command:
```
sudo apt-get install systemd
```

To check which version of systemd you have simply run the command:
```
systemd --version
```

Now let's create configuration file:
```
sudo nano /etc/systemd/system/tradfri-exporter.service
```

And paste the following into it:
```
# /etc/systemd/system/tradfri-exporter.service
[Unit]
Description=Tradfri exporter service
After=multi-user.target

[Service]
Type=simple
User=<username>
Restart=on-failure
WorkingDirectory=/home/<username>/tradfri-exporter
# Restart, but not more than once every 30s (for testing purposes)
StartLimitInterval=30
Environment=HOST_PORT=XXXX
Environment=UPDATE_INTERVAL=XXXX
ExecStart=/usr/bin/python3 main.py "<GATEWAY_IP>" -K "<SECURITY_CODE>"

[Install]
WantedBy=multi-user.target
```

Insert the environment variables (`UPDATE_INTERVAL` in seconds) and username in your OS where `<username>` is written. You also need to provide your hub's IP address `<GATEWAY_IP>` and security code `<SECURITY_CODE>`. The ExecStart flag takes in the command that you want to run. So basically the first argument is the python path (in my case it’s python3), the second argument is the path to the script that needs to be executed and further arguments are needed for script to run. Restart flag is set to always because I want to restart my service if the server gets restarted. For more information on this, you can go to this link. Now we need to reload the daemon.
```
sudo systemctl daemon-reload
```

Let’s enable our service so that it doesn’t get disabled if the server restarts.
```
sudo systemctl enable tradfri-exporter.service
```

And now let’s start our service.
```
sudo systemctl start tradfri-exporter.service
```

Now our service is up and running.

## There are several commands you can do to start, stop, restart, and check status.
To stop the service:
```
sudo systemctl stop name_of_your_service
```
To restart:
```
sudo systemctl restart name_of_your_service
```

To check status:
```
sudo systemctl status name_of_your_service
```

## References and sources
* Skabunkel's [deconz-exporter](https://github.com/Skabunkel/deconz-exporter)
* [pytradfri](https://github.com/home-assistant-libs/pytradfri) package
