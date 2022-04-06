from socket import *
from socketserver import BaseRequestHandler, UDPServer
import socketserver
from pysnmp.hlapi import *
from byte_oid import *
from parsersnmp import *
from threading import Thread
#----------------------------get request报文构造--------------------------------------
#数学归纳法构造报文,输入字节数组、类型，输出16进制字符串
def requestt(typee,bytestrr): #为简单起见，默认所有的value均为string，且在传输过程中以ascii编码
    length = len(bytestrr)
    if(length < 0xf):
        lene = '0'+hex(length)[2:]
    else:
        lene = hex(length)[2:]
    bytestr = bytestrr.hex()     #字节数组转为16进制字符串
    if(typee == "oid"):
        bytestr = "06" + lene + bytestr
    elif(typee == "seq"):
        bytestr = "30" + lene + bytestr
    elif(typee == "pdu"):
        bytestr = "a0" + lene + bytestr
    return bytestr
def makereq(oidbyte): #输入字节数组OID，字符串value
    oidrespon = requestt("oid",oidbyte)
    var1 = oidrespon + "0500"
    var1 = bytes.fromhex(var1)
    var1 = requestt("seq",var1)
    var2 = bytes.fromhex(var1)
    var2 = requestt("seq",var2)    #默认一个变量
    var2 = "020100020100020100"+var2      #request id/error-status/error-index
    var2 = bytes.fromhex(var2)
    var3 = requestt("pdu",var2)
    var3 = "02010104067075626c6963" + var3  #version/community
    var3 = bytes.fromhex(var3)
    final = requestt("seq",var3)
    return final

#--------------------------发送get request请求至连接的agent------------------------
def get_request(data,address):
    data = makereq(data)        #data必须为oid的字节数组
    #print("Get Request:",data)
    udpCliSock.sendto(bytes.fromhex(data), address)       #客户端发送消息，必须发送字节数组,将接收>的十六进制字符串转化为字节数组
    data, address = udpCliSock.recvfrom(bufsiz)        #接收回应消息，接收到的是字节数组
    print("Get Response:",data)
    return parserREP(data)

#-------------------------充当udp服务器随时接收来自agent的trap报警-------
class TimeHandler(BaseRequestHandler):
    def handle(self):
        #print('Got connection from', self.client_address)
        msg, sock = self.request
        valoid = parserREQ(msg)
        alertoid = byte_transto_oid(valoid)
        print("Trap告警：")
        print(dict[alertoid])
        print("Alert OID:",alertoid)

def watchtrap():
    print("======================Manager trap=======================")

    #接收trap报文的manager作为一个udp服务器，绑定19162端口
    serv = socketserver.ThreadingUDPServer(('127.0.0.1', 162), TimeHandler)
    serv.serve_forever()
def request():
    print("======================Manager=======================")
    print("======================请输入想要查询的oid============")
    #udp客户端连接agent并进行Get request/get response通信
    host = '127.0.0.1'
    port = 20161        #端口号
    addr = (host, port)
    print("example:1.3.6.1.2.1.1.1.0")
    oid = str(input())#1.3.6.1.2.1.1.1.0
    data = oid_transto_byte(oid)
    if(len(data)!= 0):
        val = get_request(data,addr)


if __name__ == '__main__':
    udpCliSock = socket(AF_INET, SOCK_DGRAM)    #创建客户端套接字
    dict ={"1.3.6.1.4.1.2022.4.6.0":"CPU总负载"}
    bufsiz = 1024       #接收消息的缓冲大小
    t1 = Thread(target=watchtrap)
    t2 = Thread(target=request)
    t1.start()
    t2.start()
    '''
    print("======================Manager=======================")
    print("======================请输入想要查询的oid============")
    #udp客户端连接agent并进行Get request/get response通信
    host = '127.0.0.1'
    port = 20161        #端口号
    bufsiz = 1024       #接收消息的缓冲大小
    addr = (host, port)
    udpCliSock = socket(AF_INET, SOCK_DGRAM)    #创建客户端套接字
    oid = str(input())#1.3.6.1.2.1.1.1.0
    data = oid_transto_byte(oid)
    if(len(data)!= 0):
        val = get_request(data,addr)'''