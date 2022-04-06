from socketserver import BaseRequestHandler, UDPServer
import socketserver
from socket import *
from pysnmp.hlapi import *
from byte_oid import *
from parsersnmp import *
from getoidvalue import *
from threading import *
import time
import psutil
#----------------------------get response报文构造-----------------------
#数学归纳法构造报文,输入字节数组、类型，输出16进制字符串
def response(typee,bytestrr): #为简单起见，默认所有的value均为string，且在传输过程中以ascii编码
    length = len(bytestrr)
    if(length < 0x10):
        lene = '0'+hex(length)[2:]
    else:
        lene = hex(length)[2:]
    bytestr = bytestrr.hex()     #字节数组转为16进制字符串
    if(typee == "value"):
        bytestr = "09"+lene+bytestr
    elif(typee == "oid"):
        bytestr = "06" + lene + bytestr
    elif(typee == "seq"):
        bytestr = "30" + lene + bytestr
    elif(typee == "pdu"):
        bytestr = "a2" + lene + bytestr
    return bytestr;
#----------------------------------------------------------------------
def makeres(value,oidbyte): #输入字节数组OID，字符串value
    bytestr = bytes(value,'utf-8')
    resul = response("value",bytestr)
    oidrespon = response("oid",oidbyte)
    var1 = oidrespon + resul
    var1 = bytes.fromhex(var1)
    var1 = response("seq",var1)
    #print("var1:",var1);
    var2 = bytes.fromhex(var1)
    var2 = response("seq",var2)    #默认一个变量
    var2 = "020100020100020100"+var2      #request id/error-status/error-index
    var2 = bytes.fromhex(var2)
    var3 = response("pdu",var2)
    var3 = "02010104067075626c6963" + var3      #version/community
    var3 = bytes.fromhex(var3)
    final = response("seq",var3)
    return final

#-------------------------------trap告警报文构造---------------
def trap(types,bytestrs):
    length = len(bytestrs)
    if(length < 0x10):
        lene = '0'+hex(length)[2:]
    else:
        lene = hex(length)[2:]
    bytestrs = bytestrs.hex()     #字节数组转为16进制字符串
    if(types == "value"):
        bytestrs = "04"+ lene + bytestrs
    elif(types == "oid"):
        bytestrs = "06" + lene + bytestrs
    elif(types == "seq"):
        bytestrs = "30" + lene + bytestrs
    elif(types == "pdu"):       #trap
        bytestrs = "a7" + lene + bytestrs
    return bytestrs
#---------------------------------------------------------------
def maketrap(value,oidbyte): #trap变量绑定：trap发生的时间sysuptime、trap发生的oid
    oidrespon = trap("oid",oidbyte)
    bytestr = bytes(value,'utf-8')
    resul = trap("value",bytestr)
    var1 =   oidrespon + resul
    var1 = bytes.fromhex(var1)
    var1 = trap("seq",var1)
    var2 = bytes.fromhex(var1)
    var2 = trap("seq",var2)    #默认一个变量
    var2 = "020100020100020100"+var2      #request id/error-status/error-index
    var2 = bytes.fromhex(var2)
    var3 = trap("pdu",var2)
    var3 = "02010104067075626c6963" + var3      #version/community
    var3 = bytes.fromhex(var3)
    final = trap("seq",var3)
    return final


#----------------------------Socket请求处理类的继承、派生、重写--------------
class TimeHandler(BaseRequestHandler):
    def handle(self):
        msg, sock = self.request    #msg为字节数组(bytes),一个元素为一个字节     
        #print("Get Request:",msg)
        print('Got connection from', self.client_address)
        #从get request报文中解析出对象标识符OID
        oidresult = parserREQ(msg)    #get OID
        print("oid:",oidresult)
        #将OID字节数组转为OID字符串
        stroid = byte_transto_oid(oidresult)
        print("Query OID:",stroid)
        #利用获取到的OID查询数据库，得到其对应的value值
        val = str(getOIDvalue(stroid))
        print("Query OID value:",val)
        #调用构造报文函数
        if(val != None):
            baowen  = makeres(val,oidresult)
        sock.sendto(bytes.fromhex(baowen), self.client_address)

def respon():
    print("======================Agent=======================") 
    serv = socketserver.ThreadingUDPServer(('', 20161), TimeHandler)
    serv.serve_forever()
def send_trap():
    print("======================TrapAgent=======================")
    print("======================trap请输入监控的oid==============")
    #udp客户端连接manager并进行Trap通信
    host = '127.0.0.1'
    port = 162        #端口号
    bufsiz = 1024       #接收消息的缓冲大小
    addr = (host, port)  
    print("1.3.6.1.4.1.2022.4.6.0:""CPU总负载")
    trapoid = str(input())    #监控指标的oid
    while(1):
        #-----------------------调用psutil库实现以下功能-----------------------------
        #调用trap监视函数，时刻监控数据，超标30%则调用trap报文构造函数并发送给连接的Manager
        press = psutil.cpu_percent(0) # CPU总负载
        print("CPU总负载：",press)
        if(press > 30):     #总负载大于30%，即发送trap
            timeval = str(getOIDvalue(SYSUPTIME))
            trapoid = oid_transto_byte(trapoid)  
            press = "CPU总负载："+str(press)            
            last = maketrap(timeval,trapoid)
            udpCliSock.sendto(bytes.fromhex(last), addr)
            time.sleep(5)
    #-----------------------------
            break
    print("\ntrap over!!\n")
    udpCliSock.close()
if __name__ == '__main__':    
    udpCliSock = socket(AF_INET, SOCK_DGRAM)#创建客户端套接字
    SYSUPTIME = "1.3.6.1.2.1.1.3.0"
    t1 = Thread(target=respon)
    t2 = Thread(target=send_trap)
    t1.start()
    t2.start()

    '''#--------------------------------------------------------------
    print("======================Agent=======================") 
    serv = socketserver.ThreadingUDPServer(('', 20161), TimeHandler)
    serv.serve_forever()'''
