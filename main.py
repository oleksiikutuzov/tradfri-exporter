from prometheus_client import start_http_server
from http import client, HTTPStatus
import logging
import time
import sys
import os
import tradfri
import signal
from threading import Event

from pytradfri.util import load_json, save_json
from pytradfri.error import PytradfriError
from pytradfri.api.libcoap_api import APIFactory
from pytradfri import Gateway
import uuid
import json
import argparse
import os

"""
Environment variable labels used to read values from.
HOST_PORT       Sets port to run the prometheus http server, default to 80
UPDATE_INTERVAL Sets interval between updates in seconds, default is 3600.0 seconds or 1 hour
"""
PORT_LABEL = 'HOST_PORT'
TIMEOUT_LABEL = 'UPDATE_INTERVAL'

exit = Event()

folder = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath("%s/.." % folder))

CONFIG_FILE = "tradfri_standalone_psk.conf"


def signalShuttdown(self, *args):
    exit.set()


config = {
    'host_port': 80,
    'timeout': 3600.0
}

if PORT_LABEL in os.environ:
    config['host_port'] = int(os.environ[PORT_LABEL])

if TIMEOUT_LABEL in os.environ:
    config['timeout'] = float(os.environ[TIMEOUT_LABEL])


def create_logger(scope):
    logger = logging.getLogger(scope)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%dT%H:%M:%S"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


parser = argparse.ArgumentParser()
parser.add_argument(
    "host", metavar="IP", type=str, help="IP Address of your Tradfri gateway"
)
parser.add_argument(
    "-K",
    "--key",
    dest="key",
    required=False,
    help="Security code found on your Tradfri gateway",
)
args = parser.parse_args()

if args.host not in load_json(CONFIG_FILE) and args.key is None:
    print(
        "Please provide the 'Security Code' on the back of your " "Tradfri gateway:",
        end=" ",
    )
    key = input().strip()
    if len(key) != 16:
        raise PytradfriError("Invalid 'Security Code' provided.")
    else:
        args.key = key


conf = load_json(CONFIG_FILE)

try:
    identity = conf[args.host].get("identity")
    psk = conf[args.host].get("key")
    api_factory = APIFactory(host=args.host, psk_id=identity, psk=psk)
except KeyError:
    identity = uuid.uuid4().hex
    api_factory = APIFactory(host=args.host, psk_id=identity)

    try:
        psk = api_factory.generate_psk(args.key)
        print("Generated PSK: ", psk)

        conf[args.host] = {"identity": identity, "key": psk}
        save_json(CONFIG_FILE, conf)
    except AttributeError:
        raise PytradfriError(
            "Please provide the 'Security Code' on the "
            "back of your Tradfri gateway using the "
            "-K flag."
        )

api = api_factory.request

gateway = Gateway()

devices_command = gateway.get_devices()
devices_commands = api(devices_command)
devices = api(devices_commands)


def jsonify(input):
    """Convert to json."""
    return json.dumps(
        input,
        sort_keys=True,
        indent=4,
        ensure_ascii=False,
    )


if __name__ == '__main__':
    logger = create_logger('tradfri-exporter')

    start_http_server(config['host_port'])

    container = []
    for dev in devices:
        container.append(dev.raw)
        data = json.loads(jsonify(container))

    signal.signal(signal.SIGTERM, signalShuttdown)
    signal.signal(signal.SIGHUP, signalShuttdown)
    signal.signal(signal.SIGINT, signalShuttdown)
    signal.signal(signal.SIGABRT, signalShuttdown)

    while not exit.is_set():

        tradfri.extract_metrics(logger, data)

        sleepTime = 0.0

        while (config['timeout'] > sleepTime) and not exit.is_set():
            time.sleep(0.1)
            sleepTime += 0.1

    logger.info("shutting down")
