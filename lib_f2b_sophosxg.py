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

def buildXmlRequestAddIpHostGroup(ipHostGroupName):
  request = buildXmlRequestBaseElement()
  set = ET.SubElement(request, 'Set')

  # Subelements of <Set>
  iphostgroup = ET.SubElement(set, 'IPHostGroup')

  # Subelements of <IPHostGroup>
  name = ET.SubElement(iphostgroup, 'Name')
  ipfamily = ET.SubElement(iphostgroup, 'IPFamily')

  # Define values of the elements
  name.text = ipHostGroupName

  return ET.tostring(request, encoding="unicode")

def buildXmlRequestDelIpHostGroup(ipHostGroupName):
  request = buildXmlRequestBaseElement()
  remove = ET.SubElement(request, 'Remove')

  # Subelements of <Remove>
  iphostgroup = ET.SubElement(remove, 'IPHostGroup')

  # Subelements of <IPHostGroup>
  name = ET.SubElement(iphostgroup, 'Name')

  # Define values of the elements
  name.text = ipHostGroupName

  return ET.tostring(request, encoding="unicode")

def buildXmlRequestAddIpHost(ip,ipHostGroup):
  request = buildXmlRequestBaseElement()
  set = ET.SubElement(request, 'Set')

  # Subelements of <Set>
  iphost = ET.SubElement(set, 'IPHost')

  # Subelements of <IPHost>
  name = ET.SubElement(iphost, 'Name')
  ipfamily = ET.SubElement(iphost, 'IPFamily')
  hosttype = ET.SubElement(iphost, 'HostType')
  hostgrouplist = ET.SubElement(iphost, 'HostGroupList')
  ipaddress = ET.SubElement(iphost, 'IPAddress')

  # Define values of the elements
  name.text = config["sophos_iphost_prefix"] + ip
  ipfamily.text = 'IPv4'
  hosttype.text = 'IP'
  ipaddress.text = ip

  if ipHostGroup:
    # Subelements of <HostGroupList> and define its value
    hostgroup = ET.SubElement(hostgrouplist, 'HostGroup')
    hostgroup.text = ipHostGroup

  return ET.tostring(request, encoding="unicode")

def buildXmlRequestDelIpHost(ip):
  request = buildXmlRequestBaseElement()
  remove = ET.SubElement(request, 'Remove')

  # Subelements of <Remove>
  iphost = ET.SubElement(remove, 'IPHost')

  # Subelements of <IPHost>
  name = ET.SubElement(iphost, 'Name')

  # Define values of the elements
  name.text = config["sophos_iphost_prefix"] + ip

  return ET.tostring(request, encoding="unicode")

def start():
  print("Initial setup on f2b start")
  print("Ensure IP host group", config["sophos_iphostgroup_name"], "is present")
  xmldata = buildXmlRequestAddIpHostGroup(config["sophos_iphostgroup_name"])
  response = apiCall(config["url"],xmldata)
  return 0

def stop():
  print("Cleanup on f2b stop")
  print("Do NOT clean IP host group", config["sophos_iphostgroup_name"],
    "since this may affect existing firewall rules.")
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

  # Add new IpHost as part of the IpHostGroup
  xmldata = buildXmlRequestAddIpHost(ip,config["sophos_iphostgroup_name"])
  response = apiCall(config["url"],xmldata)

  return 0

def unban(ip):
  if not isValidIp(ip):
    return 1
  print("Unblock single IP", ip)

  # Update IpHost to release any IpHostGroup bindings
  # Same request as adding an IpHost but without defining an IpHostGroup
  xmldata = buildXmlRequestAddIpHost(ip,'')
  response = apiCall(config["url"],xmldata)

  # Finally delete IpHost
  xmldata = buildXmlRequestDelIpHost(ip)
  response = apiCall(config["url"],xmldata)

  return 0
