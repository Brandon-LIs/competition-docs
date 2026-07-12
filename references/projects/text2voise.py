#  -*- coding: UTF-8 -*-

# MindPlus
# Python
import sys
import json
sys.path.append("/root/mindplus/.lib/thirdExtension/liliang-gravitysci-thirdex")
import siot
import os
from aip import AipSpeech


def synthesis(text):
  try:
    return aip_speech_client.synthesis(text,"zh", 1, aip_synthesis_option)
  except Exception:
    return aip_speech_client.synthesis(text,"zh", 1)

def saveAudio(src):
  try:
    with open(src, "wb") as f:
      return f.write(aip_synthesis_result)
  except FileNotFoundError as e:
    print(f"[文件不存在] {e}")
    return None
  except TypeError as e:
    print(f"[输入类型异常] {e}")
    return None
  except BaseException as e:
    print(f"[通用异常] {e}")
    return None

# 事件回调函数
def on_message_callback(client, userdata, msg):
    dictvoise=json.loads(str(msg.payload,encoding="utf8").replace("\n","")) 
    global aip_synthesis_result
    print (dictvoise['params'][5::])
    aip_synthesis_result = synthesis(dictvoise['params'][5::])
    saveAudio("speech.wav")
    
siot.init(client_id="7884295777555359",server="10.32.88.37",port=1883,user="siot",password="dfrobot")
aip_speech_client = AipSpeech("55500773", "cUSwAdK3eeSg6w9joWg6v4YR", "v9iimuCUM8bePbu8FNr867QVlcM2jnWW")
siot.connect()
siot.loop()
siot.set_callback(on_message_callback)
aip_synthesis_option = {"aue": 6, "per": 0, "spd": 5, "pit": 5, "vol": 5}
siot.getsubscribe(topic="aaa/b")

