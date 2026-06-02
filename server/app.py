import csv
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

CONFIG_FILE = "config.json"
latest_data = None


def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)


def ensure_runtime_dirs(config):
    csv_dir = os.path.dirname(config["csv_file"])
    log_dir = os.path.dirname(config["log_file"])

    if csv_dir:
        os.makedirs(csv_dir, exist_ok=True)

    if log_dir:
        os.makedirs(log_dir, exist_ok=True)


def get_status(temperature, humidity, config):
    reasons = []

    if temperature >= config["warning_temperature"]:
        reasons.append("温度过高")

    if humidity >= config["warning_humidity"]:
        reasons.append("湿度过高")

    if reasons:
        return "Warning", "，".join(reasons)

    return "Normal", "无异常"


def write_csv(data, config):
    csv_file = config["csv_file"]
    file_exists = False

    try:
        with open(csv_file, "r", newline="") as file:
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    with open(csv_file, "a", newline="") as file:
        fieldnames = [
            "time",
            "device_id",
            "temperature",
            "humidity",
            "status",
            "alert_reason",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)


def write_log(message, config):
    log_file = config["log_file"]
    log_line = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {message}\n'

    with open(log_file, "a") as file:
        file.write(log_line)


def read_recent_data(config, limit=10):
    csv_file = config["csv_file"]

    try:
        with open(csv_file, "r", newline="") as file:
            rows = list(csv.DictReader(file))
            return rows[-limit:]
    except FileNotFoundError:
        return []


@app.route("/")
def index():
    config = load_config()
    ensure_runtime_dirs(config)
    recent_data = read_recent_data(config)

    return render_template(
        "index.html",
        latest_data=latest_data,
        recent_data=recent_data,
        config=config,
    )


@app.route("/api/data", methods=["POST"])
def receive_data():
    global latest_data

    config = load_config()
    ensure_runtime_dirs(config)

    payload = request.get_json()

    if payload is None:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        device_id = payload["device_id"]
        temperature = float(payload["temperature"])
        humidity = float(payload["humidity"])

        if device_id != config["device_id"]:
            raise ValueError("Invalid device ID")

        status, alert_reason = get_status(temperature, humidity, config)

        latest_data = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "device_id": device_id,
            "temperature": temperature,
            "humidity": humidity,
            "status": status,
            "alert_reason": alert_reason,
        }

        write_csv(latest_data, config)
        write_log(f"Received OK: {latest_data}", config)

        return jsonify(
            {
                "message": "Data received",
                "status": status,
                "alert_reason": alert_reason,
            }
        ), 200

    except (KeyError, ValueError) as error:
        write_log(f"Receive error: {payload} | {error}", config)
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


