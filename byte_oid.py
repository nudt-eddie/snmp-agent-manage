#-------------------------oid数组进行BER编码得到byte字节数组-------
def oid_transto_byte(oidstring):
    byteoid = bytearray()
    byteoid.append(43)      #1.3
    oidstring = oidstring.split('.')
    oidstring = oidstring[2:]
    for i in oidstring:
        a = int(i)
        if(a > 127):    #该对象标识大于127，则一个字节无法完全表示，需按照以下规则分解为多个字节
            j = 0
            s = 1
            while(s != 0):      #直到s = 0后，结束循环，需要j个字节才能完全表示该数
                j = j+1
                s = a // (pow(128,j))
            for w in range(1,j+1):
                s = a // (pow(128,j-w))
                a = a - s*pow(128,j-w)
                if(w==j):
                    s = s
                else:
                    s = s+128
                #print(hex(s))
                byteoid.append(s)
        else:           #该对象标识小于128，则一个字节可以完全表示
            byteoid.append(a)
    return byteoid
#----------------------将OID字节数组解码转为oid字符串-------------------
def byte_transto_oid(oidresult):
    stroid = ""
    label = [0]*len(oidresult)
    for j in range(1,len(oidresult)):
        if((oidresult[j] > 127)or((oidresult[j] < 128)and(oidresult[j-1] > 127))):
            label[j] = 1
    if(oidresult[0] > 127):
        label[0] = 1
    for n in range(len(label)):
        w = 0
        if(label[n] == 1):
            q = n
            while(label[q] == 1):
                w = w+1
                q = q+1
            label[n] = w
    for i in range(len(oidresult)):    #根据OID编码规则将OID从字节数组转为普通字符串
        if(label[i] == 0):    #第一个字节为1则后面一字节还是其数据
            s = 0
            stroid = stroid + str(oidresult[i]) + "."
        elif(label[i] == 1):
            s = s+ oidresult[i]
            stroid = stroid + str(s) + "."
        else:
            s = s+(oidresult[i]-128)*pow(128,label[i]-1)
    stroid = "1.3"+stroid[2:-1]   #删掉最后一个.'''
    return stroid