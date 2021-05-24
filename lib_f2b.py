from lib_sophosxg import *

def start():
  print("Initial setup on f2b start")
  print("Ensure IP host group", config["sophos_iphostgroup_name"], "is present")

  # Get all elements of IpHostGroup
  xmldata = buildXmlRequestStringGetIpHostGroup()
  response = apiCall(config["url"],xmldata)

  # Parse response, search 'IPHostGroup' elements for "sophos_iphostgroup_name"
  root = ET.fromstring(response.content)

  found = False
  for hostgroup in root.findall('IPHostGroup'):
    if hostgroup.find('Name').text == config["sophos_iphostgroup_name"]:
      found = True

  # If IP host group already present, do nothing
  # Otherwise add IP host group
  if found:
    print("IP host group", config["sophos_iphostgroup_name"], "already present")
  else:
    print("Adding IP host group", config["sophos_iphostgroup_name"])
    xmldata = buildXmlRequestStringAddIpHostGroup(config["sophos_iphostgroup_name"])
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
  print("Flush (clear) all IPs, by shutdown or when stopping the jail")
  # Get all elements of IpHostGroup
  xmldata = buildXmlRequestStringGetIpHostGroup()
  response = apiCall(config["url"],xmldata)

  # Parse response, search 'IPHostGroup' elements for "sophos_iphostgroup_name"
  root = ET.fromstring(response.content)

  hostNames = list()
  for hostgroup in root.findall('IPHostGroup'):
    if hostgroup.find('Name').text == config["sophos_iphostgroup_name"]:
      hostlist = hostgroup.find('HostList')
      for host in hostlist.findall('Host'):
        hostNames.append(host.text)

  # Get all elements of IpHost
  xmldata = buildXmlRequestStringGetIpHost()
  response = apiCall(config["url"],xmldata)

  # Parse response, search 'IPHost' elements for names in hostNames
  root = ET.fromstring(response.content)

  ips = list()
  for host in root.findall('IPHost'):
    if host.find('Name').text in hostNames:
      ips.append(host.find('IPAddress').text)

  # Finally unban each ip
  for ip in ips:
    unban(ip)

  return 0

def ban(ip):
  if not isValidIp(ip):
    return 1
  print("Block single IP", ip)

  # Add new IpHost as part of the IpHostGroup
  IpHostName = config["sophos_iphost_prefix"] + ip
  xmldata = buildXmlRequestStringAddIpHost(IpHostName,ip,config["sophos_iphostgroup_name"])
  response = apiCall(config["url"],xmldata)

  return 0

def unban(ip):
  if not isValidIp(ip):
    return 1
  print("Unblock single IP", ip)

  # Update IpHost to release any IpHostGroup bindings
  # Same request as adding an IpHost but without defining an IpHostGroup
  IpHostName = config["sophos_iphost_prefix"] + ip
  xmldata = buildXmlRequestStringAddIpHost(IpHostName,ip,'')
  response = apiCall(config["url"],xmldata)

  # Finally delete IpHost
  xmldata = buildXmlRequestStringDelIpHost(IpHostName)
  response = apiCall(config["url"],xmldata)

  return 0