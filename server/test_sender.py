import json
import random
import time
import urllib.error
import urllib.request

SERVER_URL = "http://127.0.0.1:5000/api/data"

DEVICES = [
    {
        "device_id": "ESP32-ROOM-001",
        "temperature_range": (26.0, 33.0),
        "humidity_range": (55.0, 75.0),
    },
    {
        "device_id": "ESP32-ROOM-002",
        "temperature_range": (28.0, 38.0),
        "humidity_range": (60.0, 80.0),
    },
]


def generate_data(device):
    return {
        "device_id": device["device_id"],
        "temperature": round(
            random.uniform(*device["temperature_range"]), 2
        ),
        "humidity": round(
            random.uniform(*device["humidity_range"]), 2
        ),
    }


def send_data(data):
    json_data = json.dumps(data).encode("utf-8")

    request = urllib.request.Request(
        SERVER_URL,
        data=json_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            result = response.read().decode("utf-8")

            print(
                f"[成功] {data['device_id']} "
                f"温度={data['temperature']}℃ "
                f"湿度={data['humidity']}% "
                f"HTTP={response.status}"
            )
            print(f"服务器响应：{result}")

    except urllib.error.HTTPError as error:
        print(f"[HTTP错误] 状态码：{error.code}")
        print(error.read().decode("utf-8"))

    except urllib.error.URLError as error:
        print(f"[连接失败] {error.reason}")

    except TimeoutError:
        print("[超时] Flask服务器没有及时响应")


def main():
    print("双区域随机数据模拟器已启动")
    print(f"发送地址：{SERVER_URL}")
    print("按 Ctrl+C 停止\n")

    try:
        while True:
            for device in DEVICES:
                data = generate_data(device)
                send_data(data)

            print("-" * 60)
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n测试程序已停止")


if __name__ == "__main__":
    main()
