#  -*- coding: UTF-8 -*-

# MindPlus
# Python
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

uploadswitch = 0
Board().begin()

def on_buttonb_click_callback():
    u_audio.record("record.wav",3)
    with open("record.wav", 'rb') as jpg_file:
        byte_content = jpg_file.read()
    if byte_content:
        base64_bytes = base64.b64encode(byte_content) # 编码成base64字节码
        base64_string = base64_bytes.decode('utf8') # 转换成字符串
        dict_img = {"params": base64_string}
        result = json.dumps(dict_img)
        client.publish('aaa/c',result)
        print(dict_img['params']) #json.dumps()函数是将一个Python数据类型列表进行json格式的编码 
        #print("33333")   


u_gui=GUI()
u_audio = Audio()


tu=u_gui.draw_image(image="1.png",x=20,y=140)
tu.config(w=200)
print("程序，启动！")
u_gui.draw_text(text="       AI守护 +",x=1,y=5,font_size=20, color="#0000FF")



def on_connect(clinet, userdata, flags, rc):
    print("Connected with result code" + str(rc))
    client.subscribe("aaa/b")

def on_message(client, userdata, msg):
    print("待命中")
    dictxzy = json.loads(str(msg.payload, encoding="utf8")) #如果没有 encoding="utf8" ，会出现b***，json.loads()函数是将json格式数据转换为字典
    print(dictxzy)
    print(dictxzy['params'])
    if dictxzy['params'] == 'paizhao':
        print('拍照')
        #############
        #FFFFFF白，行空板清屏
        u_gui.draw_text(text="拍照",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="拍照 完成",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="       火灾警告",x=1,y=100,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="录音",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="录音 完成",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#FFFFFF")

        u_gui.draw_text(text="拍照",x=1,y=40,font_size=20, color="#0000FF")
        vd = cv2.VideoCapture()
        vd.open(0)
        while not (vd.isOpened()):
            pass
        ret, grab = vd.read()
        cv2.imwrite("Mind+.png", grab)
        vd.release()
        tu.config(image="Mind+.png")
        with open("Mind+.png", 'rb') as jpg_file:
            byte_content = jpg_file.read()
        if byte_content:
            print('拍照完成') #json.dumps()函数是将一个Python数据类型列表进行json格式的编码
            u_gui.draw_text(text="拍照 完成",x=1,y=40,font_size=20, color="#0000FF")
            
            print('尝试发送手机')
            try:
                base64_bytes = base64.b64encode(byte_content) # 编码成base64字节码
                base64_string = base64_bytes.decode('utf8') # 转换成字符串
                dict_img = {"params": base64_string}
                result = json.dumps(dict_img)
                client.publish('aaa/c',result)
                print('发送手机成功')
            except:
                print('发送手机失败')
            try:
                print('尝试上传百度')
                request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
                # 二进制方式打开图片文件
                f = open('Mind+.png', 'rb')
                img = base64.b64encode(f.read())
                #print (img)
                params = {"image":img}
                access_token = 'your-token-here'
                request_url = request_url + "?access_token=" + access_token
                headers = {'content-type': 'application/x-www-form-urlencoded'}
                response = requests.post(request_url, data=params, headers=headers)
                if response:
                    print (response.json())
                    jjstr=response.json()
                    for i in range(jjstr['result_num']):
                        #print (i)
                        if  ("火" in jjstr['result'][i]['keyword']) and (jjstr['result'][i]['score']>=0.3):
                            print (jjstr['result'][i]['keyword'])
                            print (jjstr['result'][i]['score'])                    
                    outcome=(time.strftime("%Y/%m/%d %H:%M:%S")+jjstr['result'][0]['keyword']+str(jjstr['result'][0]['score'])+jjstr['result'][1]['keyword']+str(jjstr['result'][1]['score'])+jjstr['result'][2]['keyword']+str(jjstr['result'][2]['score']))
                    #print(outcome)
                    print(outcome)
                    client.publish('aaa/g',outcome)
                    #print(jjstr['result'][1]['keyword']+jjstr['result'][1]['score'])
                    #string=(jjstr['result'][1]['keyword']+jjstr['result'][1]['score'])
                    #client.publish('aaa/g',string)
            except:
                print('上传百度失败')
    elif dictxzy['params'] == 'huozai':#火灾警告
        buzzer.play(buzzer.DADADADUM,buzzer.OnceInBackground)
        #FFFFFF白，行空板清屏
        u_gui.draw_text(text="拍照",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="拍照 完成",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="       火灾警告",x=1,y=100,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="录音",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="录音 完成",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#FFFFFF")

        u_gui.draw_text(text="       火灾警告",x=1,y=100,font_size=20, color="#FF0000")
        #FF0000红
        print('火灾警告')
        
        vd = cv2.VideoCapture()
        vd.open(0)
        while not (vd.isOpened()):
            pass
        ret, grab = vd.read()
        cv2.imwrite("Mind+.png", grab)
        vd.release()
        tu.config(image="Mind+.png")
        with open("Mind+.png", 'rb') as jpg_file:
            byte_content = jpg_file.read()
        if byte_content:
            print('拍照完成') #json.dumps()函数是将一个Python数据类型列表进行json格式的编码
            
            print('尝试发送手机')
            try:
                base64_bytes = base64.b64encode(byte_content) # 编码成base64字节码
                base64_string = base64_bytes.decode('utf8') # 转换成字符串
                dict_img = {"params": base64_string}
                result = json.dumps(dict_img)
                client.publish('aaa/c',result)
                print('发送手机成功')
            except:
                print('发送手机失败')
            try:
                print('尝试上传百度')
                request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
                # 二进制方式打开图片文件
                f = open('Mind+.png', 'rb')
                img = base64.b64encode(f.read())
                #print (img)
                params = {"image":img}
                access_token = 'your-token-here'
                request_url = request_url + "?access_token=" + access_token
                headers = {'content-type': 'application/x-www-form-urlencoded'}
                response = requests.post(request_url, data=params, headers=headers)
                if response:
                    print (response.json())
                    jjstr=response.json()
                    for i in range(jjstr['result_num']):
                        #print (i)
                        if  ("火" in jjstr['result'][i]['keyword']) and (jjstr['result'][i]['score']>=0.3):
                            print (jjstr['result'][i]['keyword'])
                            print (jjstr['result'][i]['score'])   
                            buzzer.play(buzzer.DADADADUM,buzzer.OnceInBackground)
        #FFFFFF白，行空板清屏
                            u_gui.draw_text(text="拍照",x=1,y=40,font_size=20, color="#FFFFFF")
                            u_gui.draw_text(text="拍照 完成",x=1,y=40,font_size=20, color="#FFFFFF")
                            u_gui.draw_text(text="       火灾警告",x=1,y=100,font_size=20, color="#FFFFFF")
                            u_gui.draw_text(text="录音",x=1,y=40,font_size=20, color="#FFFFFF")
                            u_gui.draw_text(text="录音 完成",x=1,y=40,font_size=20, color="#FFFFFF")
                            u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#FFFFFF")
                            u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#FFFFFF")

                            u_gui.draw_text(text="       火灾警告",x=1,y=100,font_size=20, color="#FF0000")
        #FF0000红
                            print('火灾警告')                 
                    outcome=(time.strftime("%Y/%m/%d %H:%M:%S")+jjstr['result'][0]['keyword']+str(jjstr['result'][0]['score'])+jjstr['result'][1]['keyword']+str(jjstr['result'][1]['score'])+jjstr['result'][2]['keyword']+str(jjstr['result'][2]['score']))
                    #print(outcome)
                    print(outcome)
                    client.publish('aaa/g',outcome)
                    #print(jjstr['result'][1]['keyword']+jjstr['result'][1]['score'])
                    #string=(jjstr['result'][1]['keyword']+jjstr['result'][1]['score'])
                    #client.publish('aaa/g',string)
            except:
                print('done')
    elif dictxzy['params'] == 'toohot':#高温（实际上是高湿）报警，没做行空板的显示
        print('高温报警')

    elif dictxzy['params'] == 'luying':
        print('开始录音')
        ################
        #FFFFFF白，行空板清屏
        u_gui.draw_text(text="拍照",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="拍照 完成",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="       火灾警告",x=1,y=100,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="录音",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="录音 完成",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#FFFFFF")

        u_gui.draw_text(text="录音",x=1,y=40,font_size=20, color="#0000FF")
        u_audio.record("record.wav",5)
        with open("record.wav", 'rb') as jpg_file:
           byte_content = jpg_file.read()
        if byte_content:
            base64_bytes = base64.b64encode(byte_content) # 编码成base64字节码
            base64_string = base64_bytes.decode('utf8') # 转换成字符串
            dict_img = {"params": base64_string}
            result = json.dumps(dict_img)
            client.publish('aaa/c',result)
            print('录音 完成') #json.dumps()函数是将一个Python数据类型列表进行json格式的编码
            u_gui.draw_text(text="录音 完成",x=1,y=40,font_size=20, color="#0000FF")
            
    elif dictxzy['params'] == 'kaiqi':
        #############
        #FFFFFF白，行空板清屏
        u_gui.draw_text(text="拍照",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="拍照 完成",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="       火灾警告",x=1,y=100,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="录音",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="录音 完成",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#FFFFFF")
        
        u_gui.draw_text(text="自动拍照 开",x=1,y=100,font_size=20, color="#0000FF")
        paizhaosign = 1
        while  paizhaosign==1:
            #print(datetime.datetime.now().second)
            if ((datetime.datetime.now().second == 0) or (datetime.datetime.now().second == 20) or (datetime.datetime.now().second == 40) and(paizhaosign==1)):
                print("shot")
                paizhaosign=0
                #u_gui.draw_text(text="xzy",x=1,y=10,font_size=20, color="#0000FF")
                vd = cv2.VideoCapture()
                vd.open(0)
                while not (vd.isOpened()):
                    pass
                ret, grab = vd.read()
                cv2.imwrite("Mind+.png", grab)
                vd.release()
                tu.config(image="Mind+.png")
                with open("Mind+.png", 'rb') as jpg_file:
                    byte_content = jpg_file.read()
                if byte_content:
                    base64_bytes = base64.b64encode(byte_content) # 编码成base64字节码
                    base64_string = base64_bytes.decode('utf8') # 转换成字符串
                    dict_img = {"params": base64_string}
                    result = json.dumps(dict_img)
                    client.publish('aaa/c',result)
                    print("done") #json.dumps()函数是将一个Python数据类型列表进行json格式的编码
                    #client.publish('aaa/b','{"params": "kaiqi"}')
                
                if dictxzy['params'] == 'guanbi':
                    print('关闭')
        ###############
        #FFFFFF白，行空板清屏
                    u_gui.draw_text(text="拍照",x=1,y=40,font_size=20, color="#FFFFFF")
                    u_gui.draw_text(text="拍照 完成",x=1,y=40,font_size=20, color="#FFFFFF")
                    u_gui.draw_text(text="       火灾警告",x=1,y=100,font_size=20, color="#FFFFFF")
                    u_gui.draw_text(text="录音",x=1,y=40,font_size=20, color="#FFFFFF")
                    u_gui.draw_text(text="录音 完成",x=1,y=40,font_size=20, color="#FFFFFF")
                    u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#FFFFFF")
                    u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#FFFFFF")

                    u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#0000FF")
                    paizhaosign = 0
        
    elif dictxzy['params'] == 'guanbi':
        paizhaosign = 0
        ###############
        #FFFFFF白，行空板清屏
        u_gui.draw_text(text="拍照",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="拍照 完成",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="       火灾警告",x=1,y=100,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="录音",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="录音 完成",x=1,y=40,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#FFFFFF")
        u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#FFFFFF")

        u_gui.draw_text(text="自动拍照 关",x=1,y=100,font_size=20, color="#0000FF")
        
    #elif dictxzy['params'] == 'luying':
    #    u_audio.record("record.wav",5)
    #    with open("record.wav", 'rb') as jpg_file:
    #       byte_content = jpg_file.read()
    #    if byte_content:
    #        base64_bytes = base64.b64encode(byte_content) # 编码成base64字节码
    #        base64_string = base64_bytes.decode('utf8') # 转换成字符串
    #        dict_img = {"params": base64_string}
    #        result = json.dumps(dict_img)
    #        client.publish('aaa/c',result)
    #        print(dict_img['params']) #json.dumps()函数是将一个Python数据类型列表进行json格式的编码
               
                                
    else:
        
        print("==")
        imgdata = base64.b64decode((dictxzy['params']))
        file = open('6.wav', 'wb')
        file.write(imgdata)
        file.close()
        #u_audio.play("6.wav")      
        os.system("mplayer  6.wav")
    return msg.payload

u_gui.on_b_click(on_buttonb_click_callback)
client = mqtt.Client("12345")
client.username_pw_set("siot","dfrobot")
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.173.167", 1883, 60)

#def task1():
if (button_a.is_pressed()==True):
        uploadswitch = 1
        print('1')
if (button_b.is_pressed()==True):
    uploadswitch = 0
    print('0')
if (uploadswitch == 1):
    if (datetime.datetime.now().second == 30):
        siot.publish(topic="aaa/b", data='{"params":"paizhao"}')
        print('2')

client.loop_forever()
 
def task2():
 while True:
  time.sleep(2)
  print('task2 run...')
  print(light.read())
  #print(str(temperature)+str(humidity)+str(GPIO.input(8)))
  dict_temp={"params": str(light.read())}
  result_dict_temp = json.dumps(dict_temp)
  client.publish('aaa/c',result_dict_temp)
  #print ('Temp: {0:0.1f} C Humidity: {1:0.1f} %'.format(temperature, humidity))

#th1 = threading.Thread(target = task1)
#th1.start()
#th2 = threading.Thread(target = task2)
#th2.start()

# 自定义函数

#while True:
#     ret, grab = vd.read()
#     cv2.imwrite("Mind+.png", grab)
#    tu.config(image="Mind+.png")
    #u_gui.draw_text(text="行空板",x=0,y=0,font_size=20, color="#0000FF")
#     u_audio.record("record.wav",10)
#     u_audio.play("record.wav")
#    print ("ceshi")
#    client.on_message = on_message
   # print("....")
