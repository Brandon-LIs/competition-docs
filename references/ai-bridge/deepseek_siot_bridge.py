# deepseek_mqtt_bridge.py
# 修改 Ollama 监听地址,添加系统环境变量:OLLAMA_HOST 变量值：0.0.0.0
# 自动过滤 <think> 标签及其内容，仅保留最终回答
#无法获取回答，可重试3次。严格限制120字内，要增加字请修改一下程序。
import paho.mqtt.client as mqtt
import requests
import json
import time

# ---------- 配置区域 ----------
SIOT_SERVER = "192.168.218.1"  # SIOT服务器IP
SIOT_PORT = 1883
SIOT_USER = "siot"             # 默认用户名
SIOT_PWD = "dfrobot"           # 默认密码
TOPIC_SUB = "topic/a"          # 订阅请求的topic
TOPIC_PUB = "topic/b"          # 发布回答的topic
OLLAMA_URL = "http://192.168.218.1:11434/api/chat"  # Ollama API地址
MODEL_NAME = "deepseek-r1:1.5b" # 模型名称
MAX_RETRIES = 3                # 最大重试次数
RETRY_DELAY = 2                # 重试延迟(秒)
# -----------------------------

def check_ollama_health():
    """检查Ollama服务是否健康"""
    try:
        health_url = OLLAMA_URL.replace("/api/chat", "/api/tags")
        response = requests.get(health_url, timeout=5)
        return response.status_code == 200
    except:
        return False

def clean_response(answer):
    """清理模型输出的<think>标签及推理过程"""
    if "<think>" in answer and "</think>" in answer:
        # 提取</think>后的内容，并去除前后空白
        return answer.split("</think>", 1)[-1].strip()
    return answer

def ask_deepseek(question):
    """调用Ollama生成回答并清理输出"""
    for attempt in range(MAX_RETRIES):
        try:
            payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": question}],
                "stream": False
            }
            print(f"正在向Ollama发送请求，模型：{MODEL_NAME}，问题：{question} (尝试 {attempt+1}/{MAX_RETRIES})")
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if "message" in result and "content" in result["message"]:
                raw_answer = result["message"]["content"]
                cleaned_answer = clean_response(raw_answer)
                print(f"原始回答：{raw_answer}")
                print(f"清理后回答：{cleaned_answer}")
                return cleaned_answer  # 清理后的回答
            else:
                error_msg = "Ollama返回的数据格式异常，未找到'message'或'content'"
                print(error_msg)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return error_msg
                
        except requests.exceptions.Timeout:
            error_msg = f"请求Ollama超时 (尝试 {attempt+1}/{MAX_RETRIES})"
            print(error_msg)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return "请求Ollama超时，请检查服务是否正常"
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求错误: {str(e)} (尝试 {attempt+1}/{MAX_RETRIES})"
            print(error_msg)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return f"网络错误: {str(e)}"
        except Exception as e:
            error_msg = f"调用DeepSeek失败: {str(e)} (尝试 {attempt+1}/{MAX_RETRIES})"
            print(error_msg)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return f"处理错误: {str(e)}"
    
    return "无法获取回答，请稍后重试"

def on_message(client, userdata, msg):
    """处理MQTT消息"""
    try:
        question = msg.payload.decode('utf-8')
        print(f"\n收到请求：{question}")
        
        # 检查Ollama服务状态
        if not check_ollama_health():
            print("Ollama服务不可用，等待5秒后重试...")
            time.sleep(5)
            if not check_ollama_health():
                error_msg = "Ollama服务不可用，请检查服务状态"
                print(error_msg)
                client.publish(TOPIC_PUB, error_msg, qos=0)
                return
        
        answer = ask_deepseek(question)
        print(f"生成回答：{answer}")
        
        # 确保回答不超过120字
        if len(answer) > 120:
            words = answer.split()
            if len(words) > 120:
                answer = " ".join(words[:120]) + "..."
            else:
                answer = answer[:117] + "..."
        
        # 发布回答
        client.publish(TOPIC_PUB, answer, qos=0)
        print(f"已回答至主题: {TOPIC_PUB}")
    except Exception as e:
        error_msg = f"处理消息时发生未知错误: {str(e)}"
        print(error_msg)
        client.publish(TOPIC_PUB, error_msg, qos=0)

def on_connect(client, userdata, flags, rc, properties=None):
    """MQTT连接回调"""
    if rc == 0:
        print("成功连接SIOT服务器！")
        client.subscribe(TOPIC_SUB)
        print(f"已订阅主题: {TOPIC_SUB}")
        
        # 检查Ollama服务状态
        if check_ollama_health():
            print("Ollama服务状态正常")
        else:
            print("警告: Ollama服务不可用")
    else:
        print(f"连接失败，错误码：{rc}")

def on_disconnect(client, userdata, rc, properties=None):
    """断开连接回调"""
    if rc != 0:
        print(f"意外断开连接，错误码: {rc}，尝试重新连接...")
        while True:
            try:
                client.reconnect()
                break
            except:
                print("重连失败，5秒后重试...")
                time.sleep(5)

# ---------- MQTT客户端初始化 ----------
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)  # 使用新版API
client.username_pw_set(SIOT_USER, SIOT_PWD)
client.on_message = on_message
client.on_connect = on_connect
client.on_disconnect = on_disconnect

# 设置遗嘱消息，在意外断开时通知
client.will_set(TOPIC_PUB, "MQTT桥接器已离线", qos=0)

try:
    print(f"正在连接MQTT服务器 {SIOT_SERVER}:{SIOT_PORT}...")
    client.connect(SIOT_SERVER, SIOT_PORT, 60)
    print("等待设备请求...")
    client.loop_forever()

except KeyboardInterrupt:
    client.disconnect()
    print("\n程序已安全退出")
except Exception as e:
    print(f"发生错误：{str(e)}")