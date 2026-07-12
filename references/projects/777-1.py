# 修改日期：2026-07-10  修改模型：claude-opus-4-8
# 功能：自动获取行空板局域网IP并显示；A/B/Home物理按键导航多页面（主页/每日早报/AI/控制/照片）；
#       接入DeepSeek AI（代码保留，语音聊天暂未上线）；每日60s-api资讯
from unihiker import Audio
from unihiker import GUI
import cv2
import base64
import json
import paho.mqtt.client as mqtt
import time
import os
import sys
import atexit
from pinpong.extension.unihiker import *
from pinpong.board import Board,Pin
import time
import threading
import datetime
import siot
import requests
from pinpong.board import Board,Pin
#百度的文本转语音
from aip import AipSpeech
sys.path.append("/root/mindplus/.lib/thirdExtension/liliang-gravitysci-thirdex")
#百度的文本转语音结束

# ====================== 后端逻辑 ======================
paizhaosign=1    # 启动即开启自动监控，网页端能立刻拿到照片和传感器数据
dictxzy={"params": ""}  # 初始化，防止 task2 线程启动时引用未定义
Board().begin()
u_gui=GUI()
u_audio = Audio()

def baidu_ai_up(baidu_keyword):
            try:
                print('尝试上传百度')
                request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
                f = open('Mind+.png', 'rb')
                img = base64.b64encode(f.read())
                up_siot('Mind+.png')
                show_page("photo")
                params = {"image":img}
                access_token = '24.dad871e4704c349ca724df4c569a7330.2592000.1714131176.282335-36105103'
                request_url = request_url + "?access_token=" + access_token
                headers = {'content-type': 'application/x-www-form-urlencoded'}
                response = requests.post(request_url, data=params, headers=headers)
                if response:
                    print (response.json())
                    jjstr=response.json()
                    for i in range(jjstr['result_num']):
                        if  (baidu_keyword in jjstr['result'][i]['keyword']) and (jjstr['result'][i]['score']>=0.3):
                            print (jjstr['result'][i]['keyword'])
                            print (jjstr['result'][i]['score'])
                            client.publish('aaa/j',baidu_keyword)
                    outcome=(time.strftime("%Y/%m/%d %H:%M:%S")+jjstr['result'][0]['keyword']+str(jjstr['result'][0]['score'])+jjstr['result'][1]['keyword']+str(jjstr['result'][1]['score'])+jjstr['result'][2]['keyword']+str(jjstr['result'][2]['score']))
                    print(outcome)
                    client.publish('aaa/g',outcome)
            except:
                print('上传百度失败')

def paizao_shot():
        print('拍照')
        vd = cv2.VideoCapture()
        vd.open(0)
        while not (vd.isOpened()):
            pass
        ret, grab = vd.read()
        cv2.imwrite("Mind+.png", grab)
        vd.release()

def up_siot(upfile_name):
        with open(upfile_name, 'rb') as jpg_file:
            byte_content = jpg_file.read()
        if byte_content:
            print('拍照完成')
            try:
                base64_bytes = base64.b64encode(byte_content)
                base64_string = base64_bytes.decode('utf8')
                dict_img = {"params": base64_string}
                result = json.dumps(dict_img)
                client.publish('aaa/c',result)
                print('发送手机成功')
            except:
                print('发送手机失败')

#百度的文本转语音
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
#百度的文本转语音结束

# ====================== 多页面 UI（A/B/Home 物理按键导航） ======================
BG     = "#0f1830"   # 背景
CARD   = "#1b2a47"   # 卡片
TITLE  = "#ffffff"   # 标题
TEXT   = "#bcd4ff"   # 普通文字
ACCENT = "#00e5ff"   # 强调色
WARN   = "#ffd166"   # 状态色

current_page   = "home"
scroll_y       = 0
max_scroll     = 0
busy           = False
mqtt_connected = False
current_photo  = "Mind+.png"
daily_date     = ""
daily_news     = []
daily_weiyu    = ""
PAGES          = ["home", "daily", "ai", "control"]   # 翻页顺序（不含照片页）

# ---- DeepSeek AI（代码保留，暂未接入语音） ----
DEEPSEEK_API   = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_KEY   = "sk-your-key-here"
DEEPSEEK_MODEL = "deepseek-v4-flash"

def ask_deepseek(question):
    try:
        resp = requests.post(
            DEEPSEEK_API,
            headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"},
            json={"model": DEEPSEEK_MODEL,
                  "messages": [{"role":"system","content":"你是智慧教室AI助手，用简洁中文回答。"},
                               {"role":"user","content": question}],
                  "stream": False},
            timeout=20)
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("DeepSeek error:", e)
        return f"AI请求失败：{e}"

# ---- 每日资讯（板子无外网，改由电脑端代取后回传显示） ----
def fetch_and_show_daily():
    global busy
    busy = True
    try:
        if current_page != "daily":
            return
        u_gui.fill_rect(x=8, y=50, w=224, h=170, color=BG)
        u_gui.draw_text(x=10, y=60, text="正在向电脑请求资讯...", font_size=13, color=TEXT)
        client.publish("aaa/req", "daily")
    except Exception as e:
        print("req daily err:", e)
    finally:
        busy = False

def handle_daily_msg(payload):
    global daily_date, daily_news, daily_weiyu, scroll_y, max_scroll
    try:
        j = json.loads(str(payload, encoding="utf8"))
        d = j.get("data", j)
        daily_date = str(d.get("date", ""))
        daily_news = d.get("news", [])
        daily_weiyu = d.get("weiyu", "")
        scroll_y = 0
        if current_page == "daily":
            u_gui.fill_rect(x=8, y=50, w=224, h=170, color=BG)
            render_daily()
    except Exception as e:
        print("daily msg err:", e)
        if current_page == "daily":
            u_gui.draw_text(x=10, y=90, text="资讯获取失败", font_size=12, color=WARN)

# ---- 绘制工具 ----
def draw_card(yy, line):
    u_gui.fill_rect(x=10, y=yy, w=220, h=28, color=CARD)
    u_gui.draw_text(x=18, y=yy+7, text=line, font_size=14, color=TEXT)

def hint():
    u_gui.draw_text(x=10, y=224, text="A上 B下  Home主页", font_size=11, color=WARN)

# ---- 各页面 ----
def draw_home():
    u_gui.draw_text(x=48, y=8, text="智慧教室控制中枢", font_size=18, color=TITLE)
    u_gui.draw_text(x=10, y=34, text="本机IP: "+unihiker_ip, font_size=12, color=ACCENT)
    draw_card(78,  "光照        --")
    draw_card(112, "环境音量    --")
    draw_card(146, "监控状态    --")
    draw_card(180, "MQTT       --")
    u_gui.draw_text(x=10, y=212, text="A上一页 B下一页 Home主页", font_size=11, color=WARN)
    update_home_sensors()

def draw_daily():
    u_gui.draw_text(x=55, y=8, text="每日60秒", font_size=18, color=TITLE)
    u_gui.draw_text(x=10, y=34, text="日期: 加载中...", font_size=12, color=ACCENT)
    u_gui.draw_text(x=10, y=60, text="正在获取每日资讯...", font_size=13, color=TEXT)
    hint()
    threading.Thread(target=fetch_and_show_daily).start()

def render_daily():
    global max_scroll
    u_gui.draw_text(x=55, y=8, text="每日60秒", font_size=18, color=TITLE)
    u_gui.draw_text(x=10, y=34, text="日期: "+daily_date, font_size=12, color=ACCENT)
    y = 54 - scroll_y
    for item in daily_news:
        for ln in [item[i:i+15] for i in range(0, len(item), 15)][:2]:
            u_gui.draw_text(x=10, y=y, text=ln, font_size=13, color=TEXT); y += 16
        y += 4
    for ln in [daily_weiyu[i:i+15] for i in range(0, len(daily_weiyu), 15)][:2]:
        u_gui.draw_text(x=10, y=y, text="微语: "+ln, font_size=12, color=WARN); y += 15
    max_scroll = max(0, y - 240)
    hint()

def draw_control():
    u_gui.draw_text(x=70, y=8, text="控制面板", font_size=18, color=TITLE)
    lines = ["拍照 / 录音 / 监控：", "由手机远程指令触发", "(MQTT topic: aaa/b)", "", "语音聊天：开发中", "（待接入语音识别）"]
    y = 50
    for ln in lines:
        u_gui.draw_text(x=10, y=y, text=ln, font_size=14, color=TEXT); y += 26
    hint()

def draw_ai():
    u_gui.draw_text(x=55, y=8, text="AI 对话", font_size=18, color=TITLE)
    u_gui.draw_text(x=10, y=50, text="语音聊天功能开发中", font_size=14, color=WARN)
    u_gui.draw_text(x=10, y=80, text="（待接入语音识别接口）", font_size=13, color=TEXT)
    hint()

def draw_photo():
    try:
        u_gui.draw_image(image=current_photo, x=20, y=10, w=200)
    except Exception as e:
        print("draw_photo err", e)
        u_gui.draw_text(x=20, y=100, text="(无图像)", color=TEXT)
    u_gui.draw_text(x=10, y=224, text="Home 返回主页", font_size=11, color=WARN)

def show_page(name):
    global current_page, scroll_y, max_scroll
    current_page = name
    scroll_y = 0
    max_scroll = 0
    try:
        u_gui.clear()
    except Exception:
        u_gui.fill_rect(x=0, y=0, w=240, h=240, color=BG)
    if name == "home":    draw_home()
    elif name == "daily": draw_daily()
    elif name == "ai":    draw_ai()
    elif name == "control": draw_control()
    elif name == "photo": draw_photo()

def rerender():
    try:
        u_gui.clear()
    except Exception:
        u_gui.fill_rect(x=0, y=0, w=240, h=240, color=BG)
    if current_page == "home":    draw_home()
    elif current_page == "daily": render_daily()
    elif current_page == "ai":    draw_ai()
    elif current_page == "control": draw_control()
    elif current_page == "photo": draw_photo()

# ---- 状态/内容更新 ----
def update_home_sensors():
    if current_page != "home":
        return
    try:
        lv = light.read()
        sv = u_audio.sound_level()
        draw_card(78,  "光照        " + str(lv))
        draw_card(112, "环境音量    " + str(sv))
        draw_card(146, "监控状态    " + ("开启" if paizhaosign else "关闭"))
        draw_card(180, "MQTT       " + ("已连接" if mqtt_connected else "未连接"))
    except Exception as e:
        print("sensor update err", e)

def screen_status(msg):
    if current_page != "home":
        return
    u_gui.fill_rect(x=8, y=50, w=224, h=22, color=BG)
    u_gui.draw_text(x=10, y=52, text=msg[:24], font_size=13, color=ACCENT)

def status_ai(msg):
    if current_page != "ai":
        return
    u_gui.fill_rect(x=8, y=108, w=224, h=20, color=BG)
    u_gui.draw_text(x=10, y=110, text="状态: "+msg, font_size=12, color=WARN)

def show_question(q):
    if current_page != "ai":
        return
    u_gui.fill_rect(x=8, y=38, w=224, h=26, color=BG)
    u_gui.draw_text(x=10, y=40, text="Q: "+q[:26], font_size=13, color=ACCENT)

def show_answer(a):
    if current_page != "ai":
        return
    u_gui.fill_rect(x=8, y=68, w=224, h=38, color=BG)
    lines = [a[i:i+14] for i in range(0, len(a), 14)][:2]
    for i, ln in enumerate(lines):
        u_gui.draw_text(x=10, y=70+i*18, text=ln, font_size=13, color=TEXT)

# ---- 语音聊天（代码保留，暂不接入） ----
def ai_voice():
    global busy, aip_synthesis_result, current_photo
    try:
        show_page("ai")
        status_ai("正在录音...")
        u_audio.record("xhreco.wav",5)
        status_ai("语音识别中...")
        os.system('python3 ost-fast.py')
        with open("xunfei_text.txt","r") as f:
            q = f.read().strip()
        if not q:
            status_ai("未识别到语音")
            return
        show_question(q)
        status_ai("AI思考中...")
        a = ask_deepseek(q)
        show_answer(a)
        status_ai("播放中...")
        aip_synthesis_result = synthesis(a)
        saveAudio("speech.wav")
        os.system("mplayer speech.wav")
        status_ai("完成")
    except Exception as e:
        print("ai_voice err", e)
        status_ai("出错了")
    finally:
        busy = False

# ---- A/B/Home 物理按键 ----
def on_a():
    global scroll_y
    if scroll_y > 0:
        scroll_y = max(0, scroll_y - 20)
        rerender()
    else:
        i = PAGES.index(current_page) if current_page in PAGES else 0
        show_page(PAGES[(i-1) % len(PAGES)])

def on_b():
    global scroll_y
    if scroll_y < max_scroll:
        scroll_y = min(max_scroll, scroll_y + 20)
        rerender()
    else:
        i = PAGES.index(current_page) if current_page in PAGES else len(PAGES)-1
        show_page(PAGES[(i+1) % len(PAGES)])

def save_state():
    try:
        with open("state.json", "w") as f:
            json.dump({"ip": unihiker_ip, "page": current_page,
                       "ts": time.strftime("%Y-%m-%d %H:%M:%S")}, f)
        print("状态已保存 -> state.json")
    except Exception as e:
        print("save_state err:", e)

def on_home():
    save_state()
    show_page("home")

# ====================== MQTT ======================
def on_connect(clinet, userdata, flags, rc):
    global mqtt_connected
    print("Connected with result code" + str(rc))
    mqtt_connected = True
    client.subscribe("aaa/b")
    client.subscribe("aaa/daily")

def on_message(client, userdata, msg):
    global paizhaosign, dictxzy, current_photo
    if msg.topic == "aaa/daily":
        handle_daily_msg(msg.payload)
        return
    try:
        dictxzy=json.loads(str(msg.payload,encoding="utf8").replace("\n",""))
    except Exception:
        print("on_message parse err:", str(msg.payload)[:60])
        return
    p = dictxzy.get('params', '')
    if not isinstance(p, str):
        p = str(p)
    if p == 'paizhao':
        screen_status("拍照")
        paizao_shot()
        up_siot('Mind+.png')
        if current_page=="home":
            current_photo='Mind+.png'; show_page("photo")
    elif p == 'luying':
        screen_status("录音")
        u_audio.record("record.wav",5)
        up_siot("record.wav")
    elif p[0:5] == 'kaiqi':
        paizhaosign = 1
        screen_status("自动监控")
    elif p == 'guanbi':
        paizhaosign = 0
        screen_status("自动监控关闭！")
    elif p[0:5] == 'video':
        paizao_shot()
        baidu_ai_up(p[5::])
        screen_status("监控画面AI中")
        if current_page=="home":
            current_photo='Mind+.png'; show_page("photo")
    elif p[0:5] == 'music':
        screen_status("语意分析AI中！")
        if (p[5::])!="":
            u_audio.record("xhreco.wav",5)
            os.system('python3 ost-fast.py')
            with open("xunfei_text.txt","r") as file:
               if file.read().find(p[5::])!=-1:
                   print("发现关键语意！")
                   client.publish('aaa/f',p[5::])
    elif p[0:5] == 'Ftext':
        screen_status(p[5::])
    elif p[0:5] == 'voise':
        screen_status(p[5::])
        aip_synthesis_result = synthesis(p[5::])
        saveAudio("speech.wav")
        os.system("mplayer  speech.wav")
    else:
        print("==")
        imgdata = base64.b64decode(p)
        print (len(imgdata))
        if len(imgdata)<=370000:
            file = open('6.wav', 'wb'); file.write(imgdata); file.close()
            os.system("mplayer  6.wav")
        else:
            file = open('mqtttu.png', 'wb'); file.write(imgdata); file.close()
            if current_page=="home":
                current_photo='mqtttu.png'; show_page("photo")
    return msg.payload

#百度的文本转语音
aip_speech_client = AipSpeech("55500773", "cUSwAdK3eeSg6w9joWg6v4YR", "v9iimuCUM8bePbu8FNr867QVlcM2jnWW")
aip_synthesis_option = {"aue": 6, "per": 0, "spd": 5, "pit": 5, "vol": 5}
##百度的文本转语音结束

# 自动获取行空板（本机）在局域网的IP，避免每次手动修改
def get_unihiker_ip():
    import socket, subprocess
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    finally:
        s.close()
    try:
        out = subprocess.check_output(["hostname", "-I"]).decode().split()
        for ip in out:
            if not ip.startswith("127."):
                return ip
    except Exception:
        pass
    return "127.0.0.1"

unihiker_ip = get_unihiker_ip()
print("行空板局域网IP：", unihiker_ip)

# 绑定物理按键
u_gui.on_a_click(on_a)
u_gui.on_b_click(on_b)
_home_bound = False
for _name in ("on_home_click", "on_homekey_click", "on_home_click_callback"):
    _fn = getattr(u_gui, _name, None)
    if callable(_fn):
        try:
            _fn(on_home)
            print("已绑定 Home 键:", _name)
            _home_bound = True
            break
        except Exception:
            pass
if not _home_bound:
    print("提示：未找到 Home 键绑定方法，可用 A/B 翻页回到 home 页")

show_page("home")

client = mqtt.Client("12345")
client.username_pw_set("siot","dfrobot")
client.on_connect = on_connect
client.on_message = on_message
client.connect(unihiker_ip, 1883, 60)

def task1():
  client.loop_forever()

def task2():
        global paizhaosign,dictxzy
        while True:
            while  paizhaosign==1:
                print ("task2 monitor")
                # 1) 拍照并上传到网页（无论有无关键词都拍，保证网页有画面）
                try:
                    paizao_shot()
                    up_siot('Mind+.png')
                except Exception as e:
                    print("monitor shot err:", e)
                # 2) 上报传感器数据
                try:
                    update_home_sensors()
                    lv = light.read()
                    sv = u_audio.sound_level()
                    temp = {"params": str(lv) + "~" + str(sv)}
                    client.publish('aaa/c', json.dumps(temp))
                except Exception as e:
                    print("monitor sensor err:", e)
                # 3) 有指定关键词时才做百度识别 和 语音识别
                try:
                    params = dictxzy.get("params", "")
                    amp = params.find("&")
                    kw_img = params[5:amp] if amp > 0 else ""
                    kw_voc = params[amp+1:] if amp > 0 else ""
                except Exception:
                    kw_img = kw_voc = ""
                if kw_img:
                    try:
                        baidu_ai_up(kw_img)
                    except Exception as e:
                        print("baidu err:", e)
                if kw_voc:
                    try:
                        u_audio.record("xhreco.wav",5)
                        os.system('python3 ost-fast.py')
                        with open("xunfei_text.txt","r") as file:
                            if file.read().find(kw_voc) != -1:
                                print("发现关键语意！")
                                client.publish('aaa/f', kw_voc)
                    except Exception as e:
                        print("voice err:", e)
                time.sleep(5)
            update_home_sensors()
            dict_temp={"params": str(light.read())+"~"+str(u_audio.sound_level())}
            result_dict_temp = json.dumps(dict_temp)
            client.publish('aaa/c',result_dict_temp)
            time.sleep(1)

th1 = threading.Thread(target = task1)
th1.start()
th2 = threading.Thread(target = task2)
th2.start()
