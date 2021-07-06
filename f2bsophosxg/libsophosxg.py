import requests
import re
from os import sys
import xml.etree.ElementTree as ET

class sophosxg:
  # Constructor method
  # Read and parse config file
  def __init__(self,config):
    try:
      self.config = {
        'url': config['url'],
        'verifySslCertificate': config['verifySslCertificate'],
        'user': config['user'],
        'pass': config['pass']
      }
    except KeyError:
      print("Configuration dict not valid or keys not as required.")
      sys.exit(1)

    if not self.isConfigValid(self.config):
      config = None
      sys.exit(1)

  # Checks given config for all parameters to be correct
  # Arguments: config json dict
  # Returns: True on valid, False on invalid
  def isConfigValid(self,config):
    if not re.search('^https:\/\/.+:\d{0,5}\/webconsole\/APIController$', config['url']):
      print("Config: Parameter url format not valid.")
      print("Config: Use this format: https://<IP/Domain:Port>/webconsole/APIController")
      return False

    if not isinstance(config['verifySslCertificate'], bool):
      print("Config: Parameter verifySslCertificate is not a boolean value.")
      return False

    for param in ['user', 'pass']:
      if not isinstance(config[param], str):
        print("Config: Parameter", param, "is not a string.")
        return False

    return True

  # Parse the Sophos API XML response content and extract the login status
  #   message text
  # Arguments: XML content of response
  # Returns: Login status message text, None when XML element not found
  def xml_getRespLoginStatus(self,responseContent):
    root = ET.fromstring(responseContent)
    login = root.find('Login')
    loginStatusMsg =  login.find('status').text
    return loginStatusMsg

  # Parse the Sophos API XML response content and extract the operation status,
  #   if available
  # Arguments: XML content of response
  # Returns: Tuple (Operation status code, operation status message text) when
  #   XML element found, otherwise tuple (None, None) when not found
  def xml_getRespOperationStatus(self,responseContent):
    root = ET.fromstring(responseContent)
    status =  root.find('.//Status')
    # Only extract status codes, if XML element is present in response
    if status != None:
      statusCode = status.get('code')
      statusText = status.text
      return (statusCode, statusText)

    # If no XML element is present in response, return tuple (None, None)
    return (None, None)

  # Parse the Sophos API response and determines whether the API call was
  #   successful or not
  # Arguments: response
  # Returns: True on successful, False on unsuccessful
  def isApiCallSuccessful(self,response):
    if response == None:
      return False
    # Sophos API response: Handle login status
    loginStatusText = self.xml_getRespLoginStatus(response.content)
    if loginStatusText != 'Authentication Successful':
      print('Sophos API login error: ' + loginStatusText)
      return False

    # Sophos API response: Handle operation status (if any operation done)
    operationStatusCode, operationStatusText = self.xml_getRespOperationStatus(response.content)
    # Do error handling only when operationStatusCode is available
    if operationStatusCode != None:
      # See: https://docs.sophos.com/nsg/sophos-firewall/18.0/API/index.html
      # Status 200: Configuration applied successfully.
      # Status 202: Ip Host / IP Host Group "<DynamicValue>" has been renamed to
      #   "<DynamicValue>" and updated successfully
      if not (operationStatusCode == '200' or operationStatusCode == '202'):
        print(
          'Sophos API error ' + operationStatusCode + ': ' + operationStatusText
        )
        return False

    return True

  # Execute a single API call by sending provided xmldata
  # Arguments: xmldata for request
  # Returns: response on success, None or exceptions on failure
  def apiCall(self,xmldata):
    verifySslCertificate = self.config['verifySslCertificate']
    requesturl = self.config['url'] + "?reqxml=" + xmldata

    if verifySslCertificate == False:
      # Suppress SSL verification warnings
      import urllib3
      urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
      response = requests.get(requesturl, verify=verifySslCertificate)
    except requests.exceptions.SSLError:
      print("SSLError: Probably a self-signed SSL certificate is used at the",
      "API and verifySslCertificate is set as 'True'.",
      "Try using a proper SSL certificate or setting verifySslCertificate",
      "as 'False'.")
      response = None

    return response

  # Creates an XML root element <Request>
  # Returns: Element
  def xml_getRootElement(self):
    # Create root element <Request>
    elem_root = ET.Element('Request')

    return elem_root

  # Creates a Login element <Login> as subelement of a root element
  # Arguments: Root element
  # Returns: Login element in root element
  def xml_addLoginElement(self,elem_root):
    # Create <Login> as subelement of <Request>
    elem_login = ET.SubElement(elem_root, 'Login')

    # Create subelements of <Login>
    elem_username = ET.SubElement(elem_login, 'Username')
    elem_password = ET.SubElement(elem_login, 'Password')

    # Define values of the elements <Login>
    elem_username.text = self.config['user']
    elem_password.text = self.config['pass']

    return elem_login

  # Creates a Method element as subelement of a root element
  # Arguments: Root element, Method-Name (<Get>, <Set> or <Remove>)
  # Returns: Method element in root element
  def xml_addMethodElement(self,elem_root,method):
    # Create <Get>, <Set> or <Remove> as subelement of <Request>
    elem_method = ET.SubElement(elem_root, method)

    return elem_method

  # Creates a entity element as subelement of a Method element
  # Arguments: Method element, Entity-Name (e.g. IPHost, etc.)
  # Returns: Entity element in Method element
  def xml_addEntityElement(self,elem_method,entity):
    elem_entity = ET.SubElement(elem_method, entity)

    return elem_entity

  # Creates a basic element with root and mandatory subelements
  # Arguments: Entity-Name (e.g. IPHost, etc.),
  #            Method-Name (<Get>, <Set> or <Remove>)
  # Returns: Root element, Entity element in root element
  def xml_getBaseElement(self,entity,method='Get'):
    # Get Base Element
    elem_root = self.xml_getRootElement()
    elem_login = self.xml_addLoginElement(elem_root)
    elem_method = self.xml_addMethodElement(elem_root,method)
    elem_entity = self.xml_addEntityElement(elem_method,entity)

    return elem_root, elem_entity

  # Creates xml string to add an IP host group
  # Arguments: Name of IP host group
  # Returns: xml string
  def xml_addIpHostGroup(self,ipHostGroupName):
    elem_root, elem_entity = self.xml_getBaseElement('IPHostGroup','Set')

    # Add individual elements
    elem_name = ET.SubElement(elem_entity, 'Name')
    elem_description = ET.SubElement(elem_entity, 'Description')
    elem_ipfamily = ET.SubElement(elem_entity, 'IPFamily')
    elem_name.text = ipHostGroupName
    elem_description.text =\
      "This is a Fail2ban managed group. Do not edit manually!"
    elem_ipfamily.text = 'IPv4'

    return ET.tostring(elem_root, encoding="unicode")

  # Creates xml string to remove an IP host group
  # Arguments: Name of IP host group
  # Returns: xml string
  def xml_delIpHostGroup(self,ipHostGroupName):
    elem_root, elem_entity = self.xml_getBaseElement('IPHostGroup','Remove')

    # Add individual elements
    elem_name = ET.SubElement(elem_entity, 'Name')
    elem_name.text = ipHostGroupName

    return ET.tostring(elem_root, encoding="unicode")

  # Creates xml string to add an IP host
  # Arguments: Name of IP host, IP address, IP host group name (opt)
  # Returns: xml string
  def xml_addIpHost(self,ipHostName,ip,ipHostGroupName):
    elem_root, elem_entity = self.xml_getBaseElement('IPHost','Set')

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
  def xml_delIpHost(self,ipHostName):
    elem_root, elem_entity = self.xml_getBaseElement('IPHost','Remove')

    # Add individual elements
    elem_name = ET.SubElement(elem_entity, 'Name')
    elem_name.text = ipHostName

    return ET.tostring(elem_root, encoding="unicode")

  # Creates xml string to get all IP host groups
  # Returns: xml string
  def xml_getIpHostGroup(self):
    elem_root, elem_entity = self.xml_getBaseElement('IPHostGroup')

    return ET.tostring(elem_root, encoding="unicode")

  # Creates xml string to get all IP hosts
  # Returns: xml string
  def xml_getIpHost(self):
    elem_root, elem_entity = self.xml_getBaseElement('IPHost')

    return ET.tostring(elem_root, encoding="unicode")
