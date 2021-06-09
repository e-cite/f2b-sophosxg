import xml.etree.ElementTree as ET
from lib.libf2b import f2b
from lib.libsophosxg import sophosxg
from lib.libutil import isValidIp

# Derivced class from f2b with SophosXG properties
class f2bsophosxg(f2b):
  # Constructor method creating an sophosxg object
  def __init__(self,configfile):
    self.sxg = sophosxg(configfile)

  # Method called once at the start of Fail2Ban.
  def start(self):
    print("Start: Ensure IP host group", self.sxg.config['iphostgroup_name'],
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
        if hostgroup.find('Name').text == self.sxg.config['iphostgroup_name']:
          found = True

    # If IP host group already present, do nothing
    # Otherwise add IP host group
    if found:
      print("Start: IP host group", self.sxg.config['iphostgroup_name'],
      "already available. Nothing to do.")
    else:
      print("Start: IP host group", self.sxg.config['iphostgroup_name'],
      "not available. Adding it.")
      xmldata = self.sxg.xml_addIpHostGroup(self.sxg.config['iphostgroup_name'])
      response = self.sxg.apiCall(xmldata)
      if not self.sxg.isApiCallSuccessful(response): return 1

    return 0

  # Method called once at the end of Fail2Ban
  def stop(self):
    print("Stop: Do NOT delete IP host group",
      self.sxg.config['iphostgroup_name'], "since this may affect",
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
      self.sxg.config['iphostgroup_name'])
    # Get all elements of IpHostGroup
    xmldata = self.sxg.xml_getIpHostGroup()
    response = self.sxg.apiCall(xmldata)
    if not self.sxg.isApiCallSuccessful(response): return 1

    # Parse response, search 'IPHostGroup' elements for "iphostgroup_name"
    root = ET.fromstring(response.content)

    hostNames = list()
    for hostgroup in root.findall('IPHostGroup'):
      if hostgroup.find('Name').text == self.sxg.config['iphostgroup_name']:
        hostlist = hostgroup.find('HostList')
        if hostlist:
          for host in hostlist.findall('Host'):
            hostNames.append(host.text)
        else:
          continue

    # Flush members of 'IPHostGroup', otherwise the members could not be deleted
    xmldata = self.sxg.xml_addIpHostGroup(self.sxg.config['iphostgroup_name'])
    response = self.sxg.apiCall(xmldata)
    if not self.sxg.isApiCallSuccessful(response): return 1

    # Finally delete each hostName found in IPHostGroup
    for hostName in hostNames:
      xmldata = self.sxg.xml_delIpHost(hostName)
      response = self.sxg.apiCall(xmldata)
      if not self.sxg.isApiCallSuccessful(response): return 1

    return 0

  # Function called when banning an IP.
  def ban(self,ip):
    if not isValidIp(ip): return 1
    print("Ban: Banning single IP", ip)

    # Add new IpHost as part of the IpHostGroup
    ipHostName = self.sxg.config['iphost_prefix'] + ip
    xmldata = self.sxg.xml_addIpHost(ipHostName,ip,self.sxg.config['iphostgroup_name'])
    response = self.sxg.apiCall(xmldata)
    if not self.sxg.isApiCallSuccessful(response): return 1

    return 0

  # Function called when unbanning an IP.
  def unban(self,ip):
    if not isValidIp(ip): return 1
    print("Unban: Unbanning single IP", ip)

    ipHostName = self.sxg.config['iphost_prefix'] + ip

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

    return 0
