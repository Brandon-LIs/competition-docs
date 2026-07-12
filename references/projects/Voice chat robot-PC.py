import os
import json
import paho.mqtt.client as mqtt
import base64
from XEdu.hub import Workflow as wf
from XEdu.LLM import Client # 导入库

import subprocess
# 假设你有一个B

def reduce_wav_size(input_file, output_file, sample_rate=8000, bit_depth=16, channels=1):
    # 使用 ffmpeg 命令行工具来处理音频文件
    command = [
        'ffmpeg',
        '-y',  # 添加 -y 参数以覆盖输出文件
        '-i', input_file,
        '-ar', str(sample_rate),
        '-ac', str(channels),
        '-sample_fmt', f's{bit_depth}',
        '-b:a', '32k',  # 设置音频比特率为32kbps以进一步减小文件大小
        output_file
    ]
    
    try:
        # 执行命令
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("An error occurred while processing the file:")
        print(f"Command: {e.cmd}")
        print(f"Return code: {e.returncode}")
        print(f"Command output: {e.stderr}")

# 示例用法



def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("siot/K2PQUEWAV")

def on_message(client, userdata, msg):
    msg.payload=msg.payload.decode("utf8")
    decoded_bytes = base64.b64decode(msg.payload)
    with open("quesion.wav",'wb') as file:
        file.write(decoded_bytes)
   # dictxzy = json.loads(msg.payload.decode("utf8").replace("\n", ""))
   # print(dictxzy)
    asr_model = wf(repo='yikshing/funasr-onnx-small') # 加载语音识别模型
    #text = asr_model.inference('1.mp3',record_seconds=5) # 录音3秒，保存到1.mp3
    text = asr_model.inference('quesion.wav') 
    # 识别结果在text中。
    quesion_TEXT = text[0]['preds'][0]
    #print(quesion_TEXT)
    client.publish('siot/P2KQUETEXT','->'+quesion_TEXT)

    chatbot = Client(provider='qwen',
               api_key='sk-xxx9xxx423badfb960yyy') # 实例化客户端，api_key替换为你自己的密钥
    res = chatbot.inference(quesion_TEXT) # 输入请求，执行推理并得到结果
    #print(res) # 结果输出
    client.publish('siot/P2KANWTEXT','->'+res)

    model = wf(repo=r'yikshing/edge-tts-zh') # 注意这里的路径要使用绝对路径
    res = model.inference(data=res,output='answer.mp3',gender='male')
    #print('文件已保存至：',res)
    #os.system(res)
    reduce_wav_size("answer.mp3", "answer.wav", sample_rate=8000, bit_depth=16, channels=1)
    with open("answer.wav",'rb') as music_file:
       byte_content = music_file.read()
    if byte_content:
       base64_bytes = base64.b64encode(byte_content) # 编码成base64字节码
       base64_string = base64_bytes.decode('utf8') # 转换成字符串
       client.publish('siot/P2KANWWAV','->'+base64_string)
    

client = mqtt.Client("12345")
client.username_pw_set("siot","dfrobot")
client.on_connect = on_connect
client.on_message = on_message
client.connect("10.21.229.7", 1883, 60)
client.loop_forever()

