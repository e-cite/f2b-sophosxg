from lib_util import *
import requests
import xml.etree.ElementTree as ET

# Execute a single API call by sending provided xmldata
# Arguments: xmldata for request
# Returns: None on errors
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

# Creates an XML root element <Request>
# Returns: Element
def xml_getRootElement():
  # Create root element <Request>
  elem_root = ET.Element('Request')

  return elem_root

# Creates a Login element <Login> as subelement of a root element
# Arguments: Root element
# Returns: Login element in root element
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

# Creates a Method element as subelement of a root element
# Arguments: Root element, Method-Name (<Get>, <Set> or <Remove>)
# Returns: Method element in root element
def xml_addMethodElement(elem_root,method):
  # Create <Get>, <Set> or <Remove> as subelement of <Request>
  elem_method = ET.SubElement(elem_root, method)

  return elem_method

# Creates a entity element as subelement of a Method element
# Arguments: Method element, Entity-Name (e.g. IPHost, etc.)
# Returns: Entity element in Method element
def xml_addEntityElement(elem_method,entity):
  elem_entity = ET.SubElement(elem_method, entity)

  return elem_entity

# Creates a basic element with root and mandatory subelements
# Arguments: Entity-Name (e.g. IPHost, etc.),
#            Method-Name (<Get>, <Set> or <Remove>)
# Returns: Root element, Entity element in root element
def xml_getBaseElement(entity,method='Get'):
  # Get Base Element
  elem_root = xml_getRootElement()
  elem_login = xml_addLoginElement(elem_root)
  elem_method = xml_addMethodElement(elem_root,method)
  elem_entity = xml_addEntityElement(elem_method,entity)

  return elem_root, elem_entity

# Creates xml string to add an IP host group
# Arguments: Name of IP host group
# Returns: xml string
def xml_addIpHostGroup(ipHostGroupName):
  elem_root, elem_entity = xml_getBaseElement('IPHostGroup','Set')

  # Add individual elements
  elem_name = ET.SubElement(elem_entity, 'Name')
  elem_ipfamily = ET.SubElement(elem_entity, 'IPFamily')
  elem_name.text = ipHostGroupName
  elem_ipfamily.text = 'IPv4'

  return ET.tostring(elem_root, encoding="unicode")

# Creates xml string to remove an IP host group
# Arguments: Name of IP host group
# Returns: xml string
def xml_delIpHostGroup(ipHostGroupName):
  elem_root, elem_entity = xml_getBaseElement('IPHostGroup','Remove')

  # Add individual elements
  elem_name = ET.SubElement(elem_entity, 'Name')
  elem_name.text = ipHostGroupName

  return ET.tostring(elem_root, encoding="unicode")

# Creates xml string to add an IP host
# Arguments: Name of IP host, IP address, IP host group name (opt)
# Returns: xml string
def xml_addIpHost(ipHostName,ip,ipHostGroupName):
  elem_root, elem_entity = xml_getBaseElement('IPHost','Set')

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

# Creates xml string to remove an IP host
# Arguments: Name of IP host
# Returns: xml string
def xml_delIpHost(ipHostName):
  elem_root, elem_entity = xml_getBaseElement('IPHost','Remove')

  # Add individual elements
  elem_name = ET.SubElement(elem_entity, 'Name')
  elem_name.text = ipHostName

  return ET.tostring(elem_root, encoding="unicode")

# Creates xml string to get all IP host groups
# Returns: xml string
def xml_getIpHostGroup():
  elem_root, elem_entity = xml_getBaseElement('IPHostGroup')

  return ET.tostring(elem_root, encoding="unicode")

# Creates xml string to get all IP hosts
# Returns: xml string
def xml_getIpHost():
  elem_root, elem_entity = xml_getBaseElement('IPHost')

  return ET.tostring(elem_root, encoding="unicode")
