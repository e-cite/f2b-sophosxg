from lib_util import *
import requests
import xml.etree.ElementTree as ET

def apiCall(xmldata):
  requesturl = getConfig('url') + "?reqxml=" + xmldata

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

def xml_getBaseElement():
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

def getXmlGetElement(entity):
  request = xml_getBaseElement()
  get = ET.SubElement(request, 'Get')
  ET.SubElement(get, entity)

  return request

def xml_addIpHostGroup(ipHostGroupName):
  request = xml_getBaseElement()
  set = ET.SubElement(request, 'Set')

  # Subelements of <Set>
  iphostgroup = ET.SubElement(set, 'IPHostGroup')

  # Subelements of <IPHostGroup>
  name = ET.SubElement(iphostgroup, 'Name')
  ipfamily = ET.SubElement(iphostgroup, 'IPFamily')

  # Define values of the elements
  name.text = ipHostGroupName

  return ET.tostring(request, encoding="unicode")

def xml_delIpHostGroup(ipHostGroupName):
  request = xml_getBaseElement()
  remove = ET.SubElement(request, 'Remove')

  # Subelements of <Remove>
  iphostgroup = ET.SubElement(remove, 'IPHostGroup')

  # Subelements of <IPHostGroup>
  name = ET.SubElement(iphostgroup, 'Name')

  # Define values of the elements
  name.text = ipHostGroupName

  return ET.tostring(request, encoding="unicode")

def xml_addIpHost(ipHostName,ip,ipHostGroup):
  request = xml_getBaseElement()
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
  name.text = ipHostName
  ipfamily.text = 'IPv4'
  hosttype.text = 'IP'
  ipaddress.text = ip

  if ipHostGroup:
    # Subelements of <HostGroupList> and define its value
    hostgroup = ET.SubElement(hostgrouplist, 'HostGroup')
    hostgroup.text = ipHostGroup

  return ET.tostring(request, encoding="unicode")

def xml_delIpHost(ipHostName):
  request = xml_getBaseElement()
  remove = ET.SubElement(request, 'Remove')

  # Subelements of <Remove>
  iphost = ET.SubElement(remove, 'IPHost')

  # Subelements of <IPHost>
  name = ET.SubElement(iphost, 'Name')

  # Define values of the elements
  name.text = ipHostName

  return ET.tostring(request, encoding="unicode")

def xml_getIpHostGroup():
  xmlelem = getXmlGetElement('IPHostGroup')
  return ET.tostring(xmlelem, encoding="unicode")

def xml_getIpHost():
  xmlelem = getXmlGetElement('IPHost')
  return ET.tostring(xmlelem, encoding="unicode")
