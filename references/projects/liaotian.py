import json
import websocket  # 使用websocket_client
Spark_url = "ws://spark-api.xf-yun.com/v3.5/chat"  # v3.0环境的地址
domain = "generalv3"    # v3.0版本
import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
import os
#from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import time
from unihiker import GUI

u_gui=GUI()
answer = ""
with open('hfile.txt', 'w') as f:
    f.write("")


def print_centered(text, width=80):
    """
    Print the text centered in a line of the given width.
    """
    spaces = (width - len(text)) // 2
    centered_text = ' ' * spaces + text + ' ' * spaces
    print(centered_text)

# 示例


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'xinhuoapi_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.Spark_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url

# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)

# 收到websocket关闭的处理
def on_close(ws,one,two):
    print(" ")

# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))

def run(ws, *args):
    data = json.dumps(gen_params(xinhuoappid=ws.xinhuoappid, domain= ws.domain,question=ws.question))
    ws.send(data)
    #print ((data))

# 收到websocket消息的处理
def on_message(ws, message):
    global i
    # print(message)
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        
        #print (i)
        #print (type(content))
        print(content,end ="")
        with open('hfile.txt', 'a') as f:
            f.write(content)
        
        with open('hfile.txt', 'r') as f:
            contentx = f.read().replace('\n', '')

        #print(len(contentx))
        for i in range(0,len(contentx),16):
            u_gui.draw_text(text=contentx[i:i+16],x=0,y=i,font_size=10, color="#0000FF")


        global answer
        answer += content
        #print(answer)
        if status == 2:
            ws.close()

def gen_params(xinhuoappid, domain,question):
    """
    通过appid和用户的提问来生成请参数
    """
    data = {
        "header": {
            "app_id": xinhuoappid,
            "uid": "1234"
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": 0.5,
                "max_tokens": 2048
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
    }
    return data

def SparkApimain(xinhuoappid, xinhuoapi_key, xinhuoapi_secret, Spark_url,domain, question):
    print("星火:")
    wsParam = Ws_Param(xinhuoappid, xinhuoapi_key, xinhuoapi_secret, Spark_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.xinhuoappid = xinhuoappid
    ws.question = question
    ws.domain = domain
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    #print (type(ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})))

def read_config(filename="config.json"):
    try:
        with open(filename, "r") as file:
            config_data = json.load(file)
        return config_data
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return None

if __name__ == '__main__':
    print_centered("=========接下来你就可以跟星火认知大模型对话啦=========", width=80)
    config = read_config()

    if config:
        xinhuoappid = config.get("xinhuoappid", "")
        xinhuoapi_secret = config.get("xinhuoapi_secret", "")
        xinhuoapi_key = config.get("xinhuoapi_key", "")

        if not all([xinhuoappid, xinhuoapi_secret, xinhuoapi_key]):
            print("Error: Incomplete configuration. Please provide xinhuoappid, xinhuoapi_secret, and xinhuoapi_key.")
            exit()

        # ... (your other variable assignments)

        text = []

        def get_text(role, content):
            jsoncon = {"role": role, "content": content}
            text.append(jsoncon)
            return text

        def get_length(text):
            length = 0
            for content in text:
                temp = content["content"]
                leng = len(temp)
                length += leng
            return length

        def check_len(text):
            while get_length(text) > 8000:
                del text[0]
            return text

        text.clear()  # Corrected the function call

        #while True:  # Infinite loop
            #user_input = input("\n我:")
        with open("xunfei_text.txt","r") as file:
        
        #user_input = "描述牛顿第一定律"
            user_input = file.read()
            question = check_len(get_text("user", user_input))
            spark_api_answer = ""
            print("星火:", end="")
            SparkApimain(xinhuoappid, xinhuoapi_key, xinhuoapi_secret, Spark_url, domain, question)
            text = get_text("assistant", spark_api_answer)  # Store the assistant's response
            #print(str(text))  # Uncomment if you want to print the conversation history
        #while True:
        time.sleep(15) 

    else:
        print("Exiting program due to missing configuration.")
