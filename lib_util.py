import ipaddress
import json

def getConfig(file):
  try:
    with open(file, 'r') as f:
      config = json.load(f)
    return config
  except:
    return None

configfile = 'config.json'
config = getConfig(configfile)

def isValidIp(ip):
  try:
    ret = ipaddress.ip_address(ip)
    return 1
  except:
    print("IP address is not valid. Exit.")
    return 0
