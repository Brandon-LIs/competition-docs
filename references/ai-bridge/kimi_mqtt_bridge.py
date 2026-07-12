# kimi_mqtt_bridge.py
import paho.mqtt.client as mqtt
import requests
import json

# ============= 配置区域 =============
MOONSHOT_API_KEY = "sk-your-key-here"  # 替换为你的Kimi API密钥
SIOT_HOST = "192.168.124.1"            # SIOT服务器地址（默认本地）
TOPIC_SUBSCRIBE = "topic/a"        # 订阅主题（接收板子指令）
TOPIC_PUBLISH = "topic/b"          # 发布主题（返回AI结果）
# ===================================

def ask_kimi(question):
    """调用Kimi大模型API"""
    headers = {
        "Authorization": f"Bearer {MOONSHOT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "moonshot-v1-8k",
        "messages": [{
            "role": "user",
            "content": question
        }],
        "temperature": 0.3
    }

    try:
        response = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers=headers,
            data=json.dumps(data))
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"请求失败，状态码：{response.status_code}"
    except Exception as e:
        return f"API调用异常：{str(e)}"

def on_connect(client, userdata, flags, rc):
    """MQTT连接回调"""
    print(f"Connected to SIOT with code {rc}")
    client.subscribe(TOPIC_SUBSCRIBE)

def on_message(client, userdata, msg):
    """消息到达回调"""
    try:
        payload = msg.payload.decode("utf-8")
        print(f"收到指令: {payload}")
        
        # 调用Kimi并获取响应
        response = ask_kimi(payload)
        
        # 发布到结果主题
        client.publish(TOPIC_PUBLISH, response)
        print(f"已发送响应到 {TOPIC_PUBLISH}")
    except Exception as e:
        print(f"处理消息异常: {str(e)}")

if __name__ == "__main__":
    # 初始化MQTT客户端
    client = mqtt.Client()
    client.username_pw_set("siot", "dfrobot")
    client.on_connect = on_connect
    client.on_message = on_message

    # 连接服务器
    client.connect(SIOT_HOST, 1883, 60)
    
    # 保持长连接
    print("启动MQTT-Kimi桥接服务成功...")
    client.loop_forever()