#---------------------------get request AND trap报文解析---------------------------
def parserREQ(payload):    #输入字节数组,单独访问其某项得到的为10进制表示
    codetype = payload[0]
    #print(bytes.hex(payload))
    #print("codetype:",hex(codetype))
    length = payload[1]
    if((codetype == 48)or(codetype == 160)or(codetype == 161)or(codetype == 162)or(codetype == 163)or(codetype == 164)or(codetype == 167)):  #SEQUENCE,SEQUENCE OF
        content = payload[2:2+length]
        #print("content1:",content)
        return parserREQ(content)
    if(codetype ==6):  #递归出口。。默认该报文只含一个变量，因此遇到的第一个OID也就是最后一个OID
        return payload[2:2+length]
    else:
        content = payload[2+length:]
        #print("content2:",content)
        return parserREQ(content)

#---------------------------get response报文解析-----------------------------------------
def parserREP(payload):    #输入字节数组,单独访问其某项得到的为10进制表示
    codetype = payload[0]
    #print("codetype:",hex(codetype))
    length = payload[1]
    if((codetype == 48)or(codetype == 160)or(codetype == 161)or(codetype == 162)or(codetype == 163)or(codetype == 164)or(codetype == 167)):  #SEQUENCE,SEQUENCE OF
        content = payload[2:2+length]
        #print("content1:",content)
        return parserREP(content)
    if(codetype ==9):  #递归出口。。
        return payload[2:2+length]
    else:
        content = payload[2+length:]
        #print("content2:",content)
        return parserREP(content)