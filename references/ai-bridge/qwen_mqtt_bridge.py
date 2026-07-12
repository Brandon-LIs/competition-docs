# qwen_mqtt_bridge.py
import paho.mqtt.client as mqtt
import requests
import json

# ---------- 配置区域 ----------
SIOT_SERVER = "192.168.124.1"  # SIOT服务器IP
SIOT_PORT = 1883
SIOT_USER = "siot"             # 默认用户名
SIOT_PWD = "dfrobot"           # 默认密码
TOPIC_SUB = "topic/a"          # 订阅请求的topic（接收设备消息）
TOPIC_PUB = "topic/b"          # 发布回答的topic（返回模型结果）
OLLAMA_URL = "http://192.168.124.1:11434/api/chat"  # Ollama API地址
MODEL_NAME = "qwen:1.8b"       # 模型名称
# -----------------------------

def clean_response(answer):
    """清理模型输出的冗余内容（如<think>标签）"""
    if "<think>" in answer and "</think>" in answer:
        return answer.split("</think>", 1)[-1].strip()
    return answer

def ask_qwen(question):
    """调用Qwen-1.8B生成回答"""
    try:
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": question}],
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        raw_answer = response.json()["message"]["content"]
        return clean_response(raw_answer)
    except Exception as e:
        print(f"调用Qwen失败: {str(e)}")
        return "服务暂不可用"

def on_message(client, userdata, msg):
    """处理MQTT消息"""
    question = msg.payload.decode('utf-8')
    print(f"\n收到请求：{question}")
    
    answer = ask_qwen(question)
    print(f"生成回答：{answer}")
    
    client.publish(TOPIC_PUB, answer, qos=0)

def on_connect(client, userdata, flags, rc, properties=None):
    """MQTT连接回调"""
    if rc == 0:
        print("成功连接SIOT服务器！")
        client.subscribe(TOPIC_SUB)
    else:
        print(f"连接失败，错误码：{rc}")

# ---------- MQTT客户端初始化 ----------
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(SIOT_USER, SIOT_PWD)
client.on_message = on_message
client.on_connect = on_connect

try:
    client.connect(SIOT_SERVER, SIOT_PORT, 60)
    print("等待设备请求...")
    client.loop_forever()

except KeyboardInterrupt:
    client.disconnect()
    print("\n程序已安全退出")
except Exception as e:
    print(f"发生错误：{str(e)}")