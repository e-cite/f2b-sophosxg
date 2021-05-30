import ipaddress
import json

# Open and read the config file
# Arguments: Filename
# Returns: config-dict
def readConfig(file):
  with open(file, 'r') as f:
    config = json.load(f)
  return config

# Getter function to get config value
# Arguments: Requested parameter
# Returns: Value of requested parameter
def getConfigValue(param):
  config = readConfig('config.json')
  value = config[param]
  return value

# Checker function to proof the validity of an IP address
# Arguments: IP address to be checked
# Returns: True on valid, False on invalid
def isValidIp(ip):
  try:
    ret = ipaddress.ip_address(ip)
    return True
  except ValueError:
    print("IP address is not valid.")
    return False
