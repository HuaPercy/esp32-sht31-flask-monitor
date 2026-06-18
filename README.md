# ESP32 + SHT31 + Flask Environmental Monitoring System

## Project Overview

This project is a local environmental monitoring system based on ESP32, SHT31 temperature and humidity sensor, WiFi communication and Flask web server.

The ESP32 collects temperature and humidity data from the SHT31 sensor through I2C, then uploads the data to a Flask server running on Ubuntu Linux via WiFi and HTTP. The web dashboard displays real-time environmental data, device status, threshold alerts and supports CSV data export.

## Features

- Temperature and humidity data acquisition using SHT31
- I2C communication between ESP32 and SHT31
- WiFi connection and HTTP data upload
- Flask backend running on Ubuntu Linux
- Real-time web dashboard
- Threshold alert for abnormal temperature or humidity
- Device offline detection
- CSV data export
- Local network access from PC or mobile phone

## Hardware

- ESP32 development board
- SHT31 temperature and humidity sensor
- USB cable
- Computer running Ubuntu Linux

## Software

- PlatformIO / Arduino framework
- Python
- Flask
- HTML / CSS / JavaScript
- Git

## System Architecture

```text
SHT31 Sensor
    ↓ I2C
ESP32
    ↓ WiFi + HTTP
Flask Server on Ubuntu Linux
    ↓
Web Dashboard / CSV Export

## My Contributions

- Designed the overall system architecture
- Implemented ESP32 sensor data acquisition
- Implemented WiFi and HTTP data transmission
- Built the Flask backend for data receiving and processing
- Designed the web dashboard for real-time monitoring
- Added threshold alert, offline detection and CSV export functions
- Deployed and tested the system in Ubuntu Linux environment

## Future Improvements

- Add MQTT communication
- Add SQLite database storage
- Add historical data charts
- Add multi-device support
- Improve network stability and error handling
Improve network stability and error handling
