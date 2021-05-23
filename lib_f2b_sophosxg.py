import ipaddress

def isValidIp(ip):
  try:
      ret = ipaddress.ip_address(ip)
      return 0
  except:
      return 1

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
  print("Block single IP", ip)
  return 0

def unban(ip):
  print("Unblock single IP", ip)
  return 0
