import csv
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

CONFIG_FILE = "config.json"
latest_data = None


def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)


def get_status(temperature, humidity, config):
    if temperature >= config["warning_temperature"] or humidity >= config["warning_humidity"]:
        return "Warning"
    return "Normal"


def write_csv(data, config):
    csv_file = config["csv_file"]
    file_exists = False

    try:
        with open(csv_file, "r", newline="") as file:
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    with open(csv_file, "a", newline="") as file:
        fieldnames = ["time", "device_id", "temperature", "humidity", "status"]
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
    recent_data = read_recent_data(config)

    return render_template(
        "index.html",
        latest_data=latest_data,
        recent_data=recent_data
    )


@app.route("/api/data", methods=["POST"])
def receive_data():
    global latest_data

    config = load_config()
    payload = request.get_json()

    if payload is None:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        device_id = payload["device_id"]
        temperature = float(payload["temperature"])
        humidity = float(payload["humidity"])

        if device_id != config["device_id"]:
            raise ValueError("Invalid device ID")

        status = get_status(temperature, humidity, config)

        latest_data = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "device_id": device_id,
            "temperature": temperature,
            "humidity": humidity,
            "status": status
        }

        write_csv(latest_data, config)
        write_log(f"Received OK: {latest_data}", config)

        return jsonify({"message": "Data received", "status": status}), 200

    except (KeyError, ValueError) as error:
        write_log(f"Receive error: {payload} | {error}", config)
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
