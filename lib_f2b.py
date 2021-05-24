from lib_sophosxg import *

def start():
  print("Initial setup on f2b start")
  print("Ensure IP host group", config["sophos_iphostgroup_name"], "is present")
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
  print("Flush (clear) all IPS, by shutdown or when stopping the jail")
  # Get all elements of IpHostGroup
  xmldata = buildXmlRequestStringGetIpHostGroup()
  response = apiCall(config["url"],xmldata)

  # Parse response, search 'Host' elements and add them to the list 'hosts'
  root = ET.fromstring(response.content)
  hosts = list()
  for host in root.iter('Host'):
    print("Found IP host:", host.text)
    hosts.append(host.text)

  # TODO: Call unban(name) per each list-element of hosts

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
