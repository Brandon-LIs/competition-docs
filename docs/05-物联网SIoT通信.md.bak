# 物联网 SIoT 通信 & MQTT

> ⭐ 比赛核心：MQTT通信+物联网=自动加分
> ⭐ 现场无公网=行空板建WiFi热点+电脑连热点+SIoT服务器
> ⭐ 三端架构：行空板M10 ⇄ SIoT ⇄ 手机App

---

## 一、核心概念（1分钟理解）

```
MQTT = 消息订阅机制（就像微信群）

发布者 → 往"主题(Topic)"发消息
订阅者 → 监听"主题(Topic)"收消息

Topic 就是消息通道名，比如：
  aaa/b  → 控制指令通道
  aaa/c  → 传感器数据通道
```

---

## 二、行空板M10 自建热点（现场必用！）

### 操作
```
行空板M10 → Home键 → 开关无线热点模式 → 打开无线热点

热点IP：192.168.123.1
SIoT地址：192.168.123.1:8080
MQTT端口：1883
```

### 连接流程
```
1. 行空板M10 打开热点
2. 电脑连接热点 "UNIHIKER-XXXX"
3. 手机连接热点（如需手机遥控）
4. 启动SIoT服务（下面讲）
```

> ⚠ 热点是2.4G的。如有加密类型问题（WPA/WPA2），Home键可切换加密方式。

---

## 三、启动 SIoT 服务器

### 方式1：行空板M10自启（最简单）
```
Home键 → 应用开关 → SIoT: 已启动
或
电脑访问 http://10.1.2.3/pc/network-setting → 启动服务
```

### 方式2：电脑端启动
1. 电脑上双击 `SIoT_windows_1_2.exe`（提前下载好放在U盘）
2. 浏览器打开 `http://192.168.123.1:8080`
3. 登录：
   ```
   账号：siot
   密码：dfrobot
   ```
4. 在网页上可以查看消息、管理设备

---

## 四、Mind+ 图形化 MQTT 编程

### 加载MQTT库
Mind+ → 扩展 → 官方库 → **MQTT** → 加载

> 📂 **SIoT双向通讯示例**：[M10 SIoT双向通讯](file:///Users/liboning/Desktop/科创比赛相关/学校比赛/2026诸暨备赛/2025年9月-2026年7月(国%20省%20市)创意智造培训/数字技术2_Mind+_行空板M10_(K10_探小梦_arduino_microbit_掌控板)项目备忘/27-1Mind+编程行空板M10%20SIOT双向通讯.mp)
> 📂 **M10与自带热点SIoT**：[M10自带热点SIoT](file:///Users/liboning/Desktop/科创比赛相关/学校比赛/2026诸暨备赛/2025年9月-2026年7月(国%20省%20市)创意智造培训/数字技术2_Mind+_行空板M10_(K10_探小梦_arduino_microbit_掌控板)项目备忘/27-6行空板M10与M10自带的SIOT双向通讯(启动板载热点WIFI).mp)

### 图形化积木三步走
```
第1步：连接MQTT服务器
  [连接到MQTT服务器] 地址 192.168.123.1 端口 1883
  [设置MQTT用户名 siot 密码 dfrobot]
  [订阅主题 aaa/b]

第2步：收到消息后的处理
  [当MQTT收到消息]
    → 判断主题
    → 判断内容
    → 执行对应操作

第3步：发送消息
  [MQTT发布] 主题 aaa/c 内容 {"temp":25.5}
```

---

## 五、Python MQTT 代码（完整模板）

### 发送端（行空板M10上报数据）

```python
import paho.mqtt.client as mqtt
import json
import time

SIOT_IP = "192.168.123.1"   # 行空板热点IP
SIOT_PORT = 1883
USERNAME = "siot"
PASSWORD = "dfrobot"

client = mqtt.Client("m10_device")
client.username_pw_set(USERNAME, PASSWORD)

def on_connect(client, userdata, flags, rc):
    print(f"MQTT连接成功, rc={rc}")

client.on_connect = on_connect
client.connect(SIOT_IP, SIOT_PORT, 60)

# 发送传感器数据
def send_data(temp, humi, light_val):
    data = {
        "temp": temp,
        "humi": humi,
        "light": light_val
    }
    client.publish("aaa/c", json.dumps(data))
    print(f"发送: {data}")

# 发送控制指令
def send_command(cmd):
    client.publish("aaa/b", json.dumps({"params": cmd}))

# 必须启动消息循环（后台线程）
import threading
threading.Thread(target=client.loop_forever).start()

# 主循环
while True:
    send_data(25.5, 60, 800)
    time.sleep(5)
```

### 接收端（行空板M10接收手机指令）

```python
import paho.mqtt.client as mqtt
import json

SIOT_IP = "192.168.123.1"

def on_connect(client, userdata, flags, rc):
    print("已连接MQTT")
    client.subscribe("aaa/b")     # 订阅控制指令
    client.subscribe("aaa/c")     # 订阅传感器数据

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = str(msg.payload, encoding="utf-8")
    
    try:
        data = json.loads(payload)
    except:
        print(f"消息解析失败: {payload}")
        return
    
    cmd = data.get("params", "")
    
    if cmd == "paizhao":
        print("收到拍照指令！")
        # 执行拍照...
    elif cmd == "luying":
        print("收到录音指令！")
        # 执行录音...
    elif cmd == "huozai":
        print("火灾报警！")
        # 蜂鸣器报警...
    else:
        print(f"未知指令: {cmd}")

client = mqtt.Client("m10_control")
client.username_pw_set("siot", "dfrobot")
client.on_connect = on_connect
client.on_message = on_message
client.connect(SIOT_IP, 1883, 60)
client.loop_forever()
```

### 完整的Topic设计规范

```python
# ===== Topic命名规范 =====

# 手机 → 行空板（控制指令）
CONTROL_TOPIC = "aaa/b"

# 行空板 → 手机（数据/照片上报）  
DATA_TOPIC = "aaa/c"

# 行空板 → 手机（报警通知）
ALERT_TOPIC = "aaa/j"

# ===== JSON消息格式 =====

# 简单指令
{"params": "paizhao"}        # 拍照
{"params": "luying"}         # 录音
{"params": "kaiqi"}          # 开启自动监控
{"params": "guanbi"}         # 关闭自动监控
{"params": "huozai"}         # 火灾警告
{"params": "toohot"}         # 温度过高
{"params": "voise你好"}      # 语音播报"你好"

# 传感器数据
{"temp": 25.5, "humi": 60, "light": 800}
{"params": "25.5~60~800"}    # 精简格式（温度~湿度~光线）

# 图片传输（Base64编码）
import base64
with open("photo.png", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode('utf-8')
client.publish("aaa/c", json.dumps({"params": img_base64}))
```

---

## 六、Arduino UNO + OBLOQ 物联网

Arduino通过OBLOQ物联网模块连接SIoT。

> 📂 **Arduino SIoT示例**：[arduino UNO OBLOQ SIoT](file:///Users/liboning/Desktop/科创比赛相关/学校比赛/2026诸暨备赛/2025年9月-2026年7月(国%20省%20市)创意智造培训/数字技术2_Mind+_行空板M10_(K10_探小梦_arduino_microbit_掌控板)项目备忘/27-3arduinoUNO_OBLOQ_SIOT心跳核心编码.sb3)
> 📂 **SIoT万能App APK**：[带设置的SIoT物联网-透明版](file:///Users/liboning/Desktop/科创比赛相关/学校比赛/2026诸暨备赛/2025年9月-2026年7月(国%20省%20市)创意智造培训/数字技术2_Mind+_行空板M10_(K10_探小梦_arduino_microbit_掌控板)项目备忘/28-带设置的SIoT物联网(万能).apk)

### 接线
```
Arduino UNO ─── OBLOQ模块
  5V      ─── VCC
  GND     ─── GND
  D2(RX)  ─── TX
  D3(TX)  ─── RX
```

### Arduino 代码模板

```cpp
#include <UNO_Obloq.h>
#include <SoftwareSerial.h>

SoftwareSerial softSerial(2, 3);   // RX=D2, TX=D3
UNO_Obloq olq;

// 定义MQTT主题
const String topics[5] = {
    "aaa/b",    // topic_0: 接收指令
    "aaa/c",    // topic_1: 发送数据
    "", "", ""  // topic_2~4: 备用
};

void setup() {
    softSerial.begin(9600);
    olq.startConnect(
        &softSerial,
        "WiFi名",          // 连行空板热点写 UNIHIKER-XXXX
        "WiFi密码",         // 行空板热点密码
        "siot",             // SIoT用户名
        "dfrobot",          // SIoT密码
        topics,
        "192.168.123.1",   // SIoT服务器IP
        1883                // MQTT端口
    );
}

void loop() {
    // 接收MQTT消息（topic_0 = "aaa/b"）
    if (olq.available(olq.topic_0)) {
        String msg = olq.getMessage(olq.topic_0);
        // 处理消息...
        Serial.println("收到: " + msg);
    }
    
    // 发送传感器数据（topic_1 = "aaa/c"）
    float temp = 25.5;
    float humi = 60;
    olq.publish(olq.topic_1, 
        "{\"temp\":" + String(temp) + ",\"humi\":" + String(humi) + "}");
    
    delay(2000);
}
```

---

## 七、手机App遥控（App Inventor）

### 快速方案：用现成APK
培训资料文件夹里有 `28-带设置的SIoT物联网(万能).apk`

**使用步骤**：
1. 安装APK到手机
2. 手机连接行空板热点
3. 打开App → "设置" → 填入：
   - 作品名称
   - 作者信息
   - SIoT服务器地址：`192.168.123.1`
4. 返回 → 自动连接 → 按钮遥控

### 自定义开发
见 [[06-手机端App开发(AppInventor)|手机端App开发文档]]

---

## 八、AI 大模型桥接（进阶）

### 架构
```
行空板M10 ──topic/a(问题)──► SIoT ──► 电脑端Python程序 ──► AI API
行空板M10 ◄──topic/b(答案)── SIoT ◄── 电脑端Python程序 ◄── AI API
```

> 📂 **Kimi桥接代码**：[kimi_mqtt_bridge.py](file:///Users/liboning/Desktop/科创比赛相关/学校比赛/2026诸暨备赛/2025年9月-2026年7月(国%20省%20市)创意智造培训/数字技术3_Mind+_行空板K10(项目备忘)/siot_kimi桥接ai/siot_kimi/kimi_mqtt_bridge.py)
> 📂 **DeepSeek桥接代码**：[deepseek_siot_bridge.py](file:///Users/liboning/Desktop/科创比赛相关/学校比赛/2026诸暨备赛/2025年9月-2026年7月(国%20省%20市)创意智造培训/数字技术4_mpython_乐动掌控_(掌控板1.0_掌控板2.0)项目备忘/siot_qwen或DeepSeek桥接本地ai/siot_DeepSeek/deepseek_siot_bridge.py)
> 📂 **Qwen桥接代码**：[qwen_mqtt_bridge.py](file:///Users/liboning/Desktop/科创比赛相关/学校比赛/2026诸暨备赛/2025年9月-2026年7月(国%20省%20市)创意智造培训/数字技术4_mpython_乐动掌控_(掌控板1.0_掌控板2.0)项目备忘/siot_qwen或DeepSeek桥接本地ai/siot_qwen/qwen_mqtt_bridge.py)

### 电脑端桥接代码（DeepSeek示例）

```python
import paho.mqtt.client as mqtt
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"

def on_message(client, userdata, msg):
    question = msg.payload.decode("utf-8")
    
    # 调用DeepSeek
    resp = requests.post(OLLAMA_URL, json={
        "model": "deepseek-r1:1.5b",
        "messages": [{"role": "user", "content": question}]
    })
    answer = resp.json()["message"]["content"]
    
    # 过滤<think>标签
    if "</think>" in answer:
        answer = answer.split("</think>", 1)[-1].strip()
    
    client.publish("topic/b", answer)

client = mqtt.Client()
client.username_pw_set("siot", "dfrobot")
client.on_message = on_message
client.connect("192.168.123.1", 1883, 60)
client.subscribe("topic/a")
client.loop_forever()
```

---

## 九、常见问题排查

| 问题 | 排查步骤 |
|------|----------|
| MQTT连不上 | ①WiFi是否2.4G ②IP对不对 ③SIoT启动了吗 ④用户名siot密码dfrobot |
| 热点连不上 | ①M10热点开了吗 ②加密类型切WPA2试试 |
| 消息收不到 | ①Topic名一致吗 ②订阅了吗 ③JSON格式合法吗 |
| 图片传不了 | ①Base64编码了没 ②图片太大超MQTT限制(建议<256KB) |

---

*参考：培训资料 M10 SIoT 项目备忘*
