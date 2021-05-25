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

def xml_addLoginElement(elem_root):
  # Create <Login> as subelement of <Request>
  elem_login = ET.SubElement(elem_root, 'Login')

  # Create subelements of <Login>
  elem_username = ET.SubElement(elem_login, 'Username')
  elem_password = ET.SubElement(elem_login, 'Password')

  # Define values of the elements <Login>
  elem_username.text = getConfig('user')
  elem_password.text = getConfig('pass')

  return elem_login

def xml_addMethodElement(elem_root,method):
  # Create <Get>, <Set> or <Remove> as subelement of <Request>
  elem_method = ET.SubElement(elem_root, method)

  return elem_method

def xml_getRootElement():
  # Create root element <Request>
  elem_root = ET.Element('Request')

  return elem_root

def xml_addEntityElement(elem_method,entity):
  elem_entity = ET.SubElement(elem_method, entity)

  return elem_entity

def xml_addIpHostGroup(ipHostGroupName):
  # Get Base Element
  elem_root = xml_getRootElement()
  elem_login = xml_addLoginElement(elem_root)
  elem_method = xml_addMethodElement(elem_root,'Set')
  elem_entity = xml_addEntityElement(elem_method,'IPHostGroup')

  # Add individual elements
  elem_name = ET.SubElement(elem_entity, 'Name')
  elem_ipfamily = ET.SubElement(elem_entity, 'IPFamily')
  elem_name.text = ipHostGroupName
  elem_ipfamily.text = 'IPv4'

  return ET.tostring(elem_root, encoding="unicode")

def xml_delIpHostGroup(ipHostGroupName):
  # Get Base Element
  elem_root = xml_getRootElement()
  elem_login = xml_addLoginElement(elem_root)
  elem_method = xml_addMethodElement(elem_root,'Remove')
  elem_entity = xml_addEntityElement(elem_method,'IPHostGroup')

  # Add individual elements
  elem_name = ET.SubElement(elem_entity, 'Name')
  elem_name.text = ipHostGroupName

  return ET.tostring(elem_root, encoding="unicode")

def xml_addIpHost(ipHostName,ip,ipHostGroupName):
  # Get Base Element
  elem_root = xml_getRootElement()
  elem_login = xml_addLoginElement(elem_root)
  elem_method = xml_addMethodElement(elem_root,'Set')
  elem_entity = xml_addEntityElement(elem_method,'IPHost')

  # Add individual elements
  elem_name = ET.SubElement(elem_entity, 'Name')
  elem_ipfamily = ET.SubElement(elem_entity, 'IPFamily')
  elem_hosttype = ET.SubElement(elem_entity, 'HostType')
  elem_hostgrouplist = ET.SubElement(elem_entity, 'HostGroupList')
  elem_ipaddress = ET.SubElement(elem_entity, 'IPAddress')
  elem_name.text = ipHostName
  elem_ipfamily.text = 'IPv4'
  elem_hosttype.text = 'IP'
  elem_ipaddress.text = ip
  # If ipHostGroupName is defined, add it as a subelement of elem_hostgrouplist
  if ipHostGroupName:
    elem_hostgroup = ET.SubElement(elem_hostgrouplist, 'HostGroup')
    elem_hostgroup.text = ipHostGroupName

  return ET.tostring(elem_root, encoding="unicode")

def xml_delIpHost(ipHostName):
  # Get Base Element
  elem_root = xml_getRootElement()
  elem_login = xml_addLoginElement(elem_root)
  elem_method = xml_addMethodElement(elem_root,'Remove')
  elem_entity = xml_addEntityElement(elem_method,'IPHost')

  # Add individual elements
  elem_name = ET.SubElement(elem_entity, 'Name')
  elem_name.text = ipHostName

  return ET.tostring(elem_root, encoding="unicode")

def xml_getIpHostGroup():
  elem_root = xml_getRootElement()
  elem_login = xml_addLoginElement(elem_root)
  elem_method = xml_addMethodElement(elem_root,'Get')
  elem_entity = xml_addEntityElement(elem_method,'IPHostGroup')

  return ET.tostring(elem_root, encoding="unicode")

def xml_getIpHost():
  elem_root = xml_getRootElement()
  elem_login = xml_addLoginElement(elem_root)
  elem_method = xml_addMethodElement(elem_root,'Get')
  elem_entity = xml_addEntityElement(elem_method,'IPHost')

  return ET.tostring(elem_root, encoding="unicode")
