import ipaddress
import json
import requests
import xml.etree.ElementTree as ET

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

def apiCall(url,xmldata):
  requesturl = url + "?reqxml=" + xmldata

  verifySslCertificate = False
  if verifySslCertificate == False:
    # Suppress SSL verification warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

  try:
    response = requests.get(requesturl, verify=verifySslCertificate)
    return response
  except:
    return None

def buildXmlRequestBaseElement():
  request = ET.Element('Request')

  # Subelements of <Request>
  login = ET.SubElement(request, 'Login')

  # Subelements of <Login>
  username = ET.SubElement(login, 'Username')
  password = ET.SubElement(login, 'Password')

  # Define values of the elements
  username.text = config["user"]
  password.text = config["pass"]

  return request

def buildXmlRequestAddIpHostGroup(ipHostGroup):
  return

def buildXmlRequestAddIpHost(ip,ipHostGroup):
  return

def buildXmlRequestDelIpHost(ip):
  return

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
  if not isValidIp(ip):
    return 1
  print("Block single IP", ip)
  return 0

def unban(ip):
  if not isValidIp(ip):
    return 1
  print("Unblock single IP", ip)
  return 0
