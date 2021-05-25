from lib_sophosxg import *

def start():
  print("Initial setup on f2b start")
  print("Ensure IP host group", getConfig('sophos_iphostgroup_name'), "is present")

  # Get all elements of IpHostGroup
  xmldata = xml_getIpHostGroup()
  response = apiCall(xmldata)

  # Parse response, search 'IPHostGroup' elements for "sophos_iphostgroup_name"
  root = ET.fromstring(response.content)

  found = False
  for hostgroup in root.findall('IPHostGroup'):
    if hostgroup.find('Name').text == getConfig('sophos_iphostgroup_name'):
      found = True

  # If IP host group already present, do nothing
  # Otherwise add IP host group
  if found:
    print("IP host group", getConfig('sophos_iphostgroup_name'), "already present")
  else:
    print("Adding IP host group", getConfig('sophos_iphostgroup_name'))
    xmldata = xml_addIpHostGroup(getConfig('sophos_iphostgroup_name'))
    response = apiCall(xmldata)

  return 0

def stop():
  print("Cleanup on f2b stop")
  print("Do NOT clean IP host group", getConfig('sophos_iphostgroup_name'),
    "since this may affect existing firewall rules.")
  return 0

def check():
  print("Executed before each ban")
  return 0

def flush():
  print("Flush (clear) all IPs, by shutdown or when stopping the jail")
  # Get all elements of IpHostGroup
  xmldata = xml_getIpHostGroup()
  response = apiCall(xmldata)

  # Parse response, search 'IPHostGroup' elements for "sophos_iphostgroup_name"
  root = ET.fromstring(response.content)

  hostNames = list()
  for hostgroup in root.findall('IPHostGroup'):
    if hostgroup.find('Name').text == getConfig('sophos_iphostgroup_name'):
      hostlist = hostgroup.find('HostList')
      if hostlist:
        for host in hostlist.findall('Host'):
          hostNames.append(host.text)
      else:
        continue

  # Flush members of 'IPHostGroup', otherwise the members could not be deleted
  xmldata = xml_addIpHostGroup(getConfig('sophos_iphostgroup_name'))
  response = apiCall(xmldata)

  # Finally delete each hostName found in IPHostGroup
  for hostName in hostNames:
    xmldata = xml_delIpHost(hostName)
    response = apiCall(xmldata)

  return 0

def ban(ip):
  if not isValidIp(ip):
    return 1
  print("Block single IP", ip)

  # Add new IpHost as part of the IpHostGroup
  ipHostName = getConfig('sophos_iphost_prefix') + ip
  xmldata = xml_addIpHost(ipHostName,ip,getConfig('sophos_iphostgroup_name'))
  response = apiCall(xmldata)

  return 0

def unban(ip):
  if not isValidIp(ip):
    return 1
  print("Unblock single IP", ip)

  # Update IpHost to release any IpHostGroup bindings
  # Same request as adding an IpHost but without defining an IpHostGroup
  ipHostName = getConfig('sophos_iphost_prefix') + ip
  xmldata = xml_addIpHost(ipHostName,ip,'')
  response = apiCall(xmldata)

  # Finally delete IpHost
  xmldata = xml_delIpHost(ipHostName)
  response = apiCall(xmldata)

  return 0
