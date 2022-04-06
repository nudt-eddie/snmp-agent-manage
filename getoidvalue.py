from pysnmp.hlapi import *


# --------------------------输入OID调用pysnmp查询相应的value---------------
def getOIDvalue(nameOID): 
    errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(
        SnmpEngine(),CommunityData("public"),UdpTransportTarget(("127.0.0.1", 161)),ContextData(),
        ObjectType(ObjectIdentity(nameOID))
        )
    )
    if errorIndication:
        print(errorIndication)
        return;
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        return;
    else:
        return varBinds[0][1];