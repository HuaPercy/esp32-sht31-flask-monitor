# ESP32 Indoor Monitor

## 项目名称

基于 ESP32 与 Ubuntu Flask 的局部环境温湿度无线监测系统设计

## 项目简介

本项目用于实现局部环境温湿度的无线采集、上传、存储和网页展示。

系统采用 ESP32 作为无线采集节点，后续接入 SHT31 温湿度传感器，通过 I2C 读取温湿度数据，并通过 WiFi 将数据上传到 Ubuntu 上位机。

Ubuntu 端运行 Flask 服务，负责接收 ESP32 上传的数据，完成数据解析、阈值判断、CSV 存储、日志记录和网页展示。

## 系统结构

```text
SHT31 温湿度传感器
↓ I2C
ESP32
↓ WiFi / HTTP POST
Ubuntu Flask 上位机
↓
CSV 数据文件 + log 日志文件
↓
Web 页面展示

# Day 07 - ESP32 配置分离与 Git 管理

## 学习目标

将 WiFi 密码、WiFi 名称和 Flask 服务器地址从主程序中分离，并使用 Git 管理 ESP32 PlatformIO 项目。

## 项目结构

```text
esp32-indoor-monitor/
├── src/
│   ├── main.cpp
│   └── secrets.h
├── platformio.ini
├── .gitignore
└── README.md

## Flask 服务排查

当网页或 ESP32 无法访问 Flask 时，按以下顺序检查：

1. 使用 `pgrep -af "python3 app.py"` 检查 Flask 进程。
2. 使用 `ss -lntp | grep 5000` 检查端口监听。
3. 使用 `curl http://127.0.0.1:5000` 检查 Ubuntu 本机访问。
4. 使用 `hostname -I` 检查 Ubuntu 当前 IP。
5. 检查 Flask 是否监听 `0.0.0.0`。
6. 检查 ESP32 和 Ubuntu 是否处于同一局域网。
7. 检查 ESP32 的 SERVER_URL 是否正确。
