import netaddr
import json

a = netaddr.IPNetwork("192.168.1.1/24")
print json.dumps(a)
