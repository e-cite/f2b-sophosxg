import ipaddress
import json
import re

# Open and read the config file
# Arguments: Filename
# Returns: config-dict
def readConfig(file):
  with open(file, 'r') as f:
    config = json.load(f)
  return config

# Checks given config for all parameters to be correct
# Arguments: config json dict
# Returns: True on valid, False on invalid
def isConfigValid(config):
  if not re.search('^https:\/\/.+:\d{0,5}\/webconsole\/APIController$', config['url']):
    print("Config: Parameter url format not valid.")
    print("Config: Use this format: https://<IP/Domain:Port>/webconsole/APIController")
    return False

  if not isinstance(config['verifySslCertificate'], bool):
    print("Config: Parameter verifySslCertificate is not a boolean value.")
    return False

  for param in ['user', 'pass', 'iphost_prefix', 'iphostgroup_name']:
    if not isinstance(config[param], str):
      print("Config: Parameter", param, "is not a string.")
      return False

  for param in ['iphost_prefix', 'iphostgroup_name']:
    if re.search(',', config[param]):
      print("Config: Parameter", param, "contains not allowed character ','.")
      return False

  if re.search('^#', config['iphost_prefix']):
    print("Config: Parameter iphost_prefix is not allowed to start with character '#'.")
    return False

  maxLengthOfIpv4Address = 15 # Max. length of IPv4 address
  maxLengthAllowed = 60 # Max. allowed characters for IP host name (Sophos API doc)
  if (len(config['iphost_prefix']) + maxLengthOfIpv4Address) >= maxLengthAllowed:
    return False

  return True

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
