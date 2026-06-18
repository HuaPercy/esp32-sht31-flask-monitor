from flask import Flask, jsonify, render_template, request
from datetime import datetime
import csv
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
OFFLINE_TIMEOUT = 15


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def get_file_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)


def ensure_csv_exists(csv_path):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "time",
                    "device_id",
                    "location",
                    "temperature",
                    "humidity",
                    "status",
                    "warning_reason",
                ],
            )
            writer.writeheader()


def get_status(temperature, humidity, device_config):
    temperature_warning = (
        temperature >= device_config["warning_temperature"]
    )
    humidity_warning = (
        humidity >= device_config["warning_humidity"]
    )

    if temperature_warning and humidity_warning:
        return "Warning", "温度过高、湿度过高"

    if temperature_warning:
        return "Warning", "温度过高"

    if humidity_warning:
        return "Warning", "湿度过高"

    return "Normal", "无异常"


def read_records(csv_path):
    if not os.path.exists(csv_path):
        return []

    records = []

    with open(csv_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            try:
                records.append(
                    {
                        "time": row["time"],
                        "device_id": row["device_id"],
                        "location": row.get("location", "未知位置"),
                        "temperature": float(row["temperature"]),
                        "humidity": float(row["humidity"]),
                        "status": row["status"],
                        "warning_reason": row.get(
                            "warning_reason", "无异常"
                        ),
                    }
                )
            except (ValueError, KeyError):
                continue

    return records


def write_log(log_path, message):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    with open(log_path, "a", encoding="utf-8") as file:
        file.write(
            f"{datetime.now():%Y-%m-%d %H:%M:%S} {message}\n"
        )


def build_device_views(config, records):
    device_views = []

    for device_id, device_config in config["devices"].items():
        device_records = [
            record
            for record in records
            if record["device_id"] == device_id
        ]

        latest = device_records[-1] if device_records else None
        is_offline = True
        offline_seconds = None

        if latest:
            try:
                latest_time = datetime.strptime(
                    latest["time"],
                    "%Y-%m-%d %H:%M:%S",
                )

                offline_seconds = int(
                    (datetime.now() - latest_time).total_seconds()
                )

                is_offline = offline_seconds > OFFLINE_TIMEOUT

            except ValueError:
                is_offline = True

        device_views.append(
            {
                "device_id": device_id,
                "location": device_config["location"],
                "warning_temperature": device_config[
                    "warning_temperature"
                ],
                "warning_humidity": device_config[
                    "warning_humidity"
                ],
                "latest": latest,
                "chart_records": device_records[-20:],
                "is_offline": is_offline,
                "offline_seconds": offline_seconds,
            }
        )

    return device_views


@app.route("/")
def index():
    config = load_config()
    csv_path = get_file_path(config["csv_file"])

    ensure_csv_exists(csv_path)

    records = read_records(csv_path)

    return render_template(
        "index.html",
        devices=build_device_views(config, records),
        recent_records=list(reversed(records[-20:])),
    )


@app.route("/api/dashboard", methods=["GET"])
def dashboard_data():
    config = load_config()
    csv_path = get_file_path(config["csv_file"])

    ensure_csv_exists(csv_path)
    records = read_records(csv_path)

    return jsonify(
        {
            "devices": build_device_views(config, records),
            "recent_records": list(reversed(records[-20:])),
            "server_time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }
    )


@app.route("/api/data", methods=["POST"])
def receive_data():
    config = load_config()
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "没有有效的JSON数据"}), 400

    required_fields = ["device_id", "temperature", "humidity"]
    missing_fields = [
        field for field in required_fields if field not in data
    ]

    if missing_fields:
        return jsonify(
            {
                "message": "缺少必要字段",
                "missing_fields": missing_fields,
            }
        ), 400

    device_id = str(data["device_id"])

    if device_id not in config["devices"]:
        return jsonify(
            {
                "message": "未知设备编号",
                "device_id": device_id,
            }
        ), 400

    try:
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
    except (TypeError, ValueError):
        return jsonify({"message": "温湿度格式错误"}), 400

    if not -40 <= temperature <= 125:
        return jsonify({"message": "温度超出测量范围"}), 400

    if not 0 <= humidity <= 100:
        return jsonify({"message": "湿度超出测量范围"}), 400

    device_config = config["devices"][device_id]
    location = device_config["location"]

    status, warning_reason = get_status(
        temperature,
        humidity,
        device_config,
    )

    record = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "device_id": device_id,
        "location": location,
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "status": status,
        "warning_reason": warning_reason,
    }

    csv_path = get_file_path(config["csv_file"])
    log_path = get_file_path(config["log_file"])

    ensure_csv_exists(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "time",
                "device_id",
                "location",
                "temperature",
                "humidity",
                "status",
                "warning_reason",
            ],
        )
        writer.writerow(record)

    write_log(
        log_path,
        (
            f"device={device_id} location={location} "
            f"temperature={temperature:.2f} "
            f"humidity={humidity:.2f} "
            f"status={status} reason={warning_reason}"
        ),
    )

    return jsonify(
        {
            "message": "Data received",
            "device_id": device_id,
            "location": location,
            "status": status,
            "warning_reason": warning_reason,
        }
    ), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
