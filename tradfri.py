from prometheus_client import Gauge
import json

_gauges = {
    "battery": Gauge("tradfri_device_battery", "Battery level of device in percent", ["manufacturer", "model", "name"]),
    # "humidity": Gauge("deconz_sensor_humidity", "Humidity of sensor in percent", ["manufacturer", "model", "name", "type", "uid"]),
    # "pressure": Gauge("deconz_sensor_pressure", "Air pressure in hectopascal (hPa)", ["manufacturer", "model", "name", "type", "uid"]),
    # "temperature": Gauge("deconz_sensor_temperature", "Temperature of sensor in Celsius", ["manufacturer", "model", "name", "type", "uid"]),
    # "open": Gauge("deconz_sensor_open", "Door status", ["manufacturer", "model", "name", "type", "uid"]),
}

_functionMap = {
    # 'ZHAHumidity': lambda x: _extract_basic_metric(x, 'humidity', 100),
    # 'ZHATemperature': lambda x: _extract_basic_metric(x, 'temperature', 100),
    # 'ZHAPressure': lambda x: _extract_basic_metric(x, 'pressure', 1),
    # 'ZHAOpenClose': lambda x: _extract_basic_metric_OpenClose(x, 'open'),
}


def _extract_basic_metric(metric, metricName, divider):
    value = float(metric['state'][metricName])/divider

    _gauges[metricName].labels(
        manufacturer=metric['manufacturername'],
        model=metric['modelid'],
        name=metric['name'],
        type=metric['type'],
        uid=metric['uniqueid'],
    ).set(value)


def _extract_basic_metric_OpenClose(metric, metricName):
    if metric['state'][metricName] == 'true':
        value = 1
    else:
        value = 0

    _gauges[metricName].labels(
        manufacturer=metric['manufacturername'],
        model=metric['modelid'],
        name=metric['name'],
        type=metric['type'],
        uid=metric['uniqueid'],
    ).set(value)


def extract_metrics(logger, data):
    _extract_battery(data)

    # for key in data:
    #     metric = data[key]

    #     if metric['type'] in _functionMap:
    #         _functionMap[metric['type']](metric)
    #     else:
    #         logger.info(f"Unknow metric type \"{metric['type']}\".")


def _extract_battery(data):
    processed = set()

    for device in data:
        value = 0

        if device["3"]["6"] == 3:
            name = device["9001"]
            type = device["3"]["1"]
            battery = device["3"]["9"]
            print("Battery status of " + type +
                  "(" + name + ") is " + str(battery))

            if device["9001"] in processed:
                continue

            processed.add(device["9001"])
            config = device["3"]

            value = int(device["3"]["9"])

            _gauges['battery'].labels(manufacturer=device["3"]["0"],
                                      model=device["3"]["1"], name=device["9001"]).set(value)
