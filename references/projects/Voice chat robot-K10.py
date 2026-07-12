from unihiker_k10 import screen,camera,tf_card,
from unihiker_k10 import temp_humi,light,acce
from unihiker_k10 import rgb,button
from unihiker_k10 import mic,speaker
from unihiker_k10 import wifi
from unihiker_k10 import mqttclient
import binascii
import os
import time
wifi.connect(ssid="YCYZCK2.4",psd="88898889",timeout=50000) #尝试连接wifi网络。可以不写参数名称。timeout为可选参数，表示连接超时时长，默认超时时间为10000毫秒
wifi.status() #返回网络连接状态，True表示已连接，False表示未连接
wifi.info() #返回包含当前IP地址、子网掩码、网关等信息的字符串

screen.init(dir=2)
screen.show_bg(color=0xFFFFFF)
#screen.set_width(width=5)
bt_a=button(button.a)#初始化板载按键传感器 A
bt_b=button(button.b)#初始化板载按键传感器 B

#当按键(A/B)(按下/松开)
def button_a_pressed():
    #print("button_a_pressed")
    print("begin sys recode")
    mic.recode_sys(name="quesion.wav",time=3)
    print("recode sys done")
    mqttclient.publish(topic='siot/K2PQUEWAV',content= '->'+base_64_send())#向对应主题发送消息,content为发送内容
    #print("已经发送完毕！")
    
def button_a_released():
    print("button_a_released")
    
def button_b_pressed():
    print("button_b_pressed")
    
def button_b_released():
    print("button_b_released")

bt_a.event_pressed = button_a_pressed
bt_a.event_released = button_a_released
bt_b.event_pressed = button_b_pressed
bt_b.event_released = button_b_released

screen.draw_text(text="Voice chat robot",x=60,y=127,font_size=27,color=0xFF0000)

screen.show_draw()
time.sleep(2)
#screen.clear()

def base_64_send():
    with open("quesion.wav", 'rb') as jpg_file:
        byte_content = jpg_file.read()
    if byte_content:
        encoded_data = binascii.b2a_base64(byte_content,newline=False)
        base64_string = encoded_data.decode('utf8') # bytes类型转换成字符串
        return base64_string

# def decode_base64():
#     decoded_data = binascii.a2b_base64(received_1ffdf0jpLa()(('ascii')))
#     with open("voice.wav",'w') as file:
#         file.write(decoded_data)

def received_P2KANWTEXT():
    msg=mqttclient.message(topic='siot/P2KANWTEXT')
    print(msg)
    
def received_P2KQUETEXT():
    msg=mqttclient.message(topic='siot/P2KQUETEXT')
    print(msg)
    
def received_P2KANWWAV():
    msg=mqttclient.message(topic='siot/P2KANWWAV')
    #decode_base64()
    #print(msg)
    msgb=msg.encode('ascii')
    decoded_data = binascii.a2b_base64(msgb)
    with open("answer.wav",'w') as file:
        file.write(decoded_data)
    speaker.play_sys_music("answer.wav")
    
mqttclient.connect(server= "10.21.229.7",
                   port=1883, 
                   client_id="",
                   user= "siot" ,
                   psd= "dfrobot") #阻塞运行，默认超时时间为3秒
mqttclient.connected() #返回连接状态


mqttclient.received (topic='siot/P2KANWTEXT', #对应主题收到消息时，回调函数
                     callback=received_P2KANWTEXT) #通过callback指定回调函数

mqttclient.received (topic='siot/P2KANWWAV', #对应主题收到消息时，回调函数
                     callback=received_P2KANWWAV) #通过callback指定回调函数

mqttclient.received (topic='siot/P2KQUETEXT', #对应主题收到消息时，回调函数
                     callback=received_P2KQUETEXT) #通过callback指定回调函数

while True:
    pass