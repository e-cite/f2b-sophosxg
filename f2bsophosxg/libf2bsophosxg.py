import xml.etree.ElementTree as ET
import ipaddress
import re
from os import sys
from f2bsophosxg.libf2b import f2b
from f2bsophosxg.libsophosxg import sophosxg

# Derivced class from f2b with SophosXG properties
class f2bsophosxg(f2b):
  # Constructor method creating an sophosxg object
  def __init__(self,config):
    try:
      self.config = {
        'iphost_prefix': config['iphost_prefix'],
        'iphostgroup_name': config['iphostgroup_name']
      }
    except KeyError:
      print("Configuration dict not valid or keys not as required.")
      sys.exit(1)

    if not self.isConfigValid(self.config):
      config = None
      sys.exit(1)

    self.sxg = sophosxg(config)

  # Checks given config for all parameters to be correct
  # Arguments: config json dict
  # Returns: True on valid, False on invalid
  def isConfigValid(self,config):
    for param in ['iphost_prefix', 'iphostgroup_name']:
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

  # Method called once at the start of Fail2Ban.
  def start(self):
    print("Start: Ensure IP host group", self.config['iphostgroup_name'],
      "is available.")

    # Get all elements of IpHostGroup
    xmldata = self.sxg.xml_getIpHostGroup()
    response = self.sxg.apiCall(xmldata)
    if not self.sxg.isApiCallSuccessful(response): return 1

    # Parse response, search 'IPHostGroup' elements for "iphostgroup_name"
    root = ET.fromstring(response.content)

    found = False
    for hostgroup in root.findall('IPHostGroup'):
      # Bugfix: When no IP host group is available
      # (hostgroup.find('Name') = None),
      # then accessing hostgroup.find('Name').text will fail!
      if hostgroup.find('Name') is not None:
        if hostgroup.find('Name').text == self.config['iphostgroup_name']:
          found = True

    # If IP host group already present, do nothing
    # Otherwise add IP host group
    if found:
      print("Start: IP host group", self.config['iphostgroup_name'],
      "already available. Nothing to do.")
    else:
      print("Start: IP host group", self.config['iphostgroup_name'],
      "not available. Adding it.")
      xmldata = self.sxg.xml_addIpHostGroup(self.config['iphostgroup_name'])
      response = self.sxg.apiCall(xmldata)
      if not self.sxg.isApiCallSuccessful(response): return 1
    print("Start: Successfully ensured IP host group",
      self.config['iphostgroup_name'], "is available.")
    return 0

  # Method called once at the end of Fail2Ban
  def stop(self):
    print("Stop: Do NOT delete IP host group",
      self.config['iphostgroup_name'], "since this may affect",
      "existing firewall rules.")
    return 0

  # Method called once before each actionban command
  def check(self):
    print("Check: There is nothing to check.")
    return 0

  # Function called once to flush (clear) all IPS, by shutdown
  # (resp. by stop of the jail or this action)
  def flush(self):
    print("Flush: Flushing all IPs in IP host group",
      self.config['iphostgroup_name'])
    # Get all elements of IpHostGroup
    xmldata = self.sxg.xml_getIpHostGroup()
    response = self.sxg.apiCall(xmldata)
    if not self.sxg.isApiCallSuccessful(response): return 1

    # Parse response, search 'IPHostGroup' elements for "iphostgroup_name"
    root = ET.fromstring(response.content)

    hostNames = list()
    for hostgroup in root.findall('IPHostGroup'):
      if hostgroup.find('Name').text == self.config['iphostgroup_name']:
        hostlist = hostgroup.find('HostList')
        if hostlist:
          for host in hostlist.findall('Host'):
            hostNames.append(host.text)
        else:
          continue
    if hostNames == []:
      print("Flush: IP host group", self.config['iphostgroup_name'],
        "not present or empty. Nothing to do.")
      return 0

    # Flush members of 'IPHostGroup', otherwise the members could not be deleted
    xmldata = self.sxg.xml_addIpHostGroup(self.config['iphostgroup_name'])
    response = self.sxg.apiCall(xmldata)
    if not self.sxg.isApiCallSuccessful(response): return 1

    # Finally delete each hostName found in IPHostGroup
    for hostName in hostNames:
      xmldata = self.sxg.xml_delIpHost(hostName)
      response = self.sxg.apiCall(xmldata)
      if not self.sxg.isApiCallSuccessful(response): return 1
    print("Flush: Successfully flushed all IPs in IP host group",
      self.config['iphostgroup_name'])
    return 0

  # Function called when banning an IP.
  def ban(self,ip):
    if not self.__isValidIp(ip): return 1
    print("Ban: Banning single IP", ip)

    # Add new IpHost as part of the IpHostGroup
    ipHostName = self.config['iphost_prefix'] + ip
    xmldata = self.sxg.xml_addIpHost(ipHostName,ip,self.config['iphostgroup_name'])
    response = self.sxg.apiCall(xmldata)
    if not self.sxg.isApiCallSuccessful(response): return 1
    print("Ban: Successfully banned single IP", ip)
    return 0

  # Function called when unbanning an IP.
  def unban(self,ip):
    if not self.__isValidIp(ip): return 1
    print("Unban: Unbanning single IP", ip)

    ipHostName = self.config['iphost_prefix'] + ip

    # Get all elements of IP host
    xmldata = self.sxg.xml_getIpHost()
    response = self.sxg.apiCall(xmldata)
    if not self.sxg.isApiCallSuccessful(response): return 1

    # Parse response, search 'IPHost' elements for "ipHostName"
    root = ET.fromstring(response.content)

    # Searching ipHostName in response to check whether its already available
    found = False
    for host in root.findall('IPHost'):
      if host.find('Name').text == ipHostName:
        found = True

    if not found:
      print("Unban: IP host", ip, "not banned. Nothing to unban.")
      return 0
    # Otherwise (host present), we have to delete it

    # Update IpHost to release any IpHostGroup bindings
    # Same request as adding an IpHost but without defining an IpHostGroup
    xmldata = self.sxg.xml_addIpHost(ipHostName,ip,'')
    response = self.sxg.apiCall(xmldata)
    if not self.sxg.isApiCallSuccessful(response): return 1

    # Finally delete IpHost
    xmldata = self.sxg.xml_delIpHost(ipHostName)
    response = self.sxg.apiCall(xmldata)
    if not self.sxg.isApiCallSuccessful(response): return 1
    print("Unban: Successfully unbanned single IP", ip)
    return 0

  # Checker function to proof the validity of an IP address
  # Arguments: IP address to be checked
  # Returns: True on valid, False on invalid
  def __isValidIp(self,ip):
    try:
      ret = ipaddress.ip_address(ip)
      return True
    except ValueError:
      print("IP address is not valid.")
      return False
