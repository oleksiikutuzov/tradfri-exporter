# tradfri-exporter
Export IKEA Tradfri devices battery status to Prometheus

## Installation

It is considered you already have python installed. Install required packages

```
pip3 install pytradfri 
```
Then install `coap-client`
```
git clone https://github.com/home-assistant-libs/pytradfri 
sudo ./pytradfri/script/install-coap-client.sh
```
Set permissons to `tradfri-exporter` folder
```
chmod 755 tradfri-exporter
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
Restart=always
Environment=HOST_PORT=XXXX
Environment=UPDATE_INTERVAL=XXXX
ExecStart=/usr/bin/python3 /home/<username>/tradfri-exporter/main.py "<GATEWAY_IP>" -K <SECURITY_CODE>

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
