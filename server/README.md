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
