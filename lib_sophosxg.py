from lib_util import *
import requests
import xml.etree.ElementTree as ET

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

def buildXmlBaseElement():
  request = ET.Element('Request')

  # Subelements of <Request>
  login = ET.SubElement(request, 'Login')

  # Subelements of <Login>
  username = ET.SubElement(login, 'Username')
  password = ET.SubElement(login, 'Password')

  # Define values of the elements
  username.text = getConfig('user')
  password.text = getConfig('pass')

  return request

def buildXmlRequestStringAddIpHostGroup(ipHostGroupName):
  request = buildXmlBaseElement()
  set = ET.SubElement(request, 'Set')

  # Subelements of <Set>
  iphostgroup = ET.SubElement(set, 'IPHostGroup')

  # Subelements of <IPHostGroup>
  name = ET.SubElement(iphostgroup, 'Name')
  ipfamily = ET.SubElement(iphostgroup, 'IPFamily')

  # Define values of the elements
  name.text = ipHostGroupName

  return ET.tostring(request, encoding="unicode")

def buildXmlRequestStringDelIpHostGroup(ipHostGroupName):
  request = buildXmlBaseElement()
  remove = ET.SubElement(request, 'Remove')

  # Subelements of <Remove>
  iphostgroup = ET.SubElement(remove, 'IPHostGroup')

  # Subelements of <IPHostGroup>
  name = ET.SubElement(iphostgroup, 'Name')

  # Define values of the elements
  name.text = ipHostGroupName

  return ET.tostring(request, encoding="unicode")

def buildXmlRequestStringAddIpHost(IpHostName,ip,ipHostGroup):
  request = buildXmlBaseElement()
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
  name.text = IpHostName
  ipfamily.text = 'IPv4'
  hosttype.text = 'IP'
  ipaddress.text = ip

  if ipHostGroup:
    # Subelements of <HostGroupList> and define its value
    hostgroup = ET.SubElement(hostgrouplist, 'HostGroup')
    hostgroup.text = ipHostGroup

  return ET.tostring(request, encoding="unicode")

def buildXmlRequestStringDelIpHost(IpHostName):
  request = buildXmlBaseElement()
  remove = ET.SubElement(request, 'Remove')

  # Subelements of <Remove>
  iphost = ET.SubElement(remove, 'IPHost')

  # Subelements of <IPHost>
  name = ET.SubElement(iphost, 'Name')

  # Define values of the elements
  name.text = IpHostName

  return ET.tostring(request, encoding="unicode")

def buildXmlRequestStringGetIpHostGroup():
  request = buildXmlBaseElement()
  get = ET.SubElement(request, 'Get')

  # Subelements of <Get>
  iphostgroup = ET.SubElement(get, 'IPHostGroup')

  # Subelements of <IPHostGroup>
  name = ET.SubElement(iphostgroup, 'Name')

  return ET.tostring(request, encoding="unicode")

def buildXmlRequestStringGetIpHost():
  request = buildXmlBaseElement()
  get = ET.SubElement(request, 'Get')

  # Subelements of <Get>
  iphost = ET.SubElement(get, 'IPHost')

  # Subelements of <IPHost>
  name = ET.SubElement(iphost, 'Name')

  return ET.tostring(request, encoding="unicode")
