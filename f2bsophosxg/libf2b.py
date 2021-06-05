import xml.etree.ElementTree as ET
from f2bsophosxg.config import config
from f2bsophosxg.libutil import isValidIp
from f2bsophosxg.libsophosxg import (
  isApiCallSuccessful,
  apiCall,
  xml_addIpHostGroup,
  xml_addIpHost,
  xml_delIpHost,
  xml_getIpHostGroup
)

# Function called once at the start of Fail2Ban.
def start():
  print("Start: Ensure IP host group", config['iphostgroup_name'],
    "is available.")

  # Get all elements of IpHostGroup
  xmldata = xml_getIpHostGroup()
  response = apiCall(xmldata)
  if not isApiCallSuccessful(response): return 1

  # Parse response, search 'IPHostGroup' elements for "iphostgroup_name"
  root = ET.fromstring(response.content)

  found = False
  for hostgroup in root.findall('IPHostGroup'):
    # Bugfix: When no IP host group is available
    # (hostgroup.find('Name') = None),
    # then accessing hostgroup.find('Name').text will fail!
    if hostgroup.find('Name') is not None:
      if hostgroup.find('Name').text == config['iphostgroup_name']:
        found = True

  # If IP host group already present, do nothing
  # Otherwise add IP host group
  if found:
    print("Start: IP host group", config['iphostgroup_name'],
    "already available. Nothing to do.")
  else:
    print("Start: IP host group", config['iphostgroup_name'],
    "not available. Adding it.")
    xmldata = xml_addIpHostGroup(config['iphostgroup_name'])
    response = apiCall(xmldata)
    if not isApiCallSuccessful(response): return 1

  return 0

# Function called once at the end of Fail2Ban
def stop():
  print("Stop: Do NOT delete IP host group",
    config['iphostgroup_name'], "since this may affect",
    "existing firewall rules.")
  return 0

# Function called once before each actionban command
def check():
  print("Check: There is nothing to check.")
  return 0

# Function called once to flush (clear) all IPS, by shutdown
# (resp. by stop of the jail or this action)
def flush():
  print("Flush: Flushing all IPs in IP host group",
    config['iphostgroup_name'])
  # Get all elements of IpHostGroup
  xmldata = xml_getIpHostGroup()
  response = apiCall(xmldata)
  if not isApiCallSuccessful(response): return 1

  # Parse response, search 'IPHostGroup' elements for "iphostgroup_name"
  root = ET.fromstring(response.content)

  hostNames = list()
  for hostgroup in root.findall('IPHostGroup'):
    if hostgroup.find('Name').text == config['iphostgroup_name']:
      hostlist = hostgroup.find('HostList')
      if hostlist:
        for host in hostlist.findall('Host'):
          hostNames.append(host.text)
      else:
        continue

  # Flush members of 'IPHostGroup', otherwise the members could not be deleted
  xmldata = xml_addIpHostGroup(config['iphostgroup_name'])
  response = apiCall(xmldata)
  if not isApiCallSuccessful(response): return 1

  # Finally delete each hostName found in IPHostGroup
  for hostName in hostNames:
    xmldata = xml_delIpHost(hostName)
    response = apiCall(xmldata)
    if not isApiCallSuccessful(response): return 1

  return 0

# Function called when banning an IP.
def ban(ip):
  if not isValidIp(ip): return 1
  print("Ban: Banning single IP", ip)

  # Add new IpHost as part of the IpHostGroup
  ipHostName = config['iphost_prefix'] + ip
  xmldata = xml_addIpHost(ipHostName,ip,config['iphostgroup_name'])
  response = apiCall(xmldata)
  if not isApiCallSuccessful(response): return 1

  return 0

# Function called when unbanning an IP.
def unban(ip):
  if not isValidIp(ip): return 1
  print("Unban: Unbanning single IP", ip)

  # Update IpHost to release any IpHostGroup bindings
  # Same request as adding an IpHost but without defining an IpHostGroup
  ipHostName = config['iphost_prefix'] + ip
  xmldata = xml_addIpHost(ipHostName,ip,'')
  response = apiCall(xmldata)
  if not isApiCallSuccessful(response): return 1

  # Finally delete IpHost
  xmldata = xml_delIpHost(ipHostName)
  response = apiCall(xmldata)
  if not isApiCallSuccessful(response): return 1

  return 0
