import ipaddress
import json

def isValidIp(ip):
  try:
    ret = ipaddress.ip_address(ip)
    return 1
  except:
    print("IP address is not valid. Exit.")
    return 0

def readConfig(file):
  try:
    with open(file, 'r') as f:
      config = json.load(f)
    return config
  except:
    return None

def start():
  print("Initial setup on f2b start")
  return 0

def stop():
  print("Cleanup on f2b stop")
  return 0

def check():
  print("Executed before each ban")
  return 0

def flush():
  print("Flush (clear) all IPS, by shutdown or when stopping the jail")
  return 0

def ban(ip):
  if isValidIp(ip):
    print("Block single IP", ip)
    return 0
  return 1

def unban(ip):
  if isValidIp(ip):
    print("Unblock single IP", ip)
    return 0
  return 1
