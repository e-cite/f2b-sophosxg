import ipaddress
import json

# Open and read the config file
# Arguments: Filename
# Returns: config-dict or None on errors
def readConfig(file):
  try:
    with open(file, 'r') as f:
      config = json.load(f)
    return config
  except:
    return None

# Getter function to get config parameters
# Arguments: Requested parameter
# Returns: Value of requested parameter
def getConfig(param):
  config = readConfig('config.json')
  return config[param]

# Checker function to proof the validity of an IP address
# Arguments: IP address to be checked
# Returns: 1 on valid, 0 on invalid
def isValidIp(ip):
  try:
    ret = ipaddress.ip_address(ip)
    return 1
  except:
    print("IP address is not valid. Exit.")
    return 0
