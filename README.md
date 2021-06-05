# Fail2ban Sophos XG API
Access the Sophos XG API from Fail2ban to block hosts on perimeter firewall

This repository contains a program and a small python library to call the
Sophos XG API from Fail2ban. With this, you can enable Fail2ban to block
malicious hosts not on the internal host firewall, but on the perimeter
firewall.

## Usage
```shell
$ python3 f2b-sophosxg.py --help
usage: f2b-sophosxg.py [-h] [--ip IP] {start,stop,check,flush,ban,unban}

f2b-sophosxg: Access SophosXG API from fail2ban to block hosts on perimeter
firewall.

positional arguments:
  {start,stop,check,flush,ban,unban}
                        Action to execute

optional arguments:
  -h, --help            show this help message and exit
  --ip IP               IPv4 address, required for action 'ban' or 'unban'
```

## Overview
Fail2ban generally uses these commands (called "actions") to handle the
blockings:
- `actionstart`: command executed on demand at the first ban or at the start of
  Fail2Ban
- `actionstop`: command executed at the stop of jail (or at the end of
  Fail2Ban)
- `actionflush`: command executed once to flush (clear) all IPS, by shutdown
  (resp. by stop of the jail or this action)
- `actioncheck`: command executed once before each actionban command
- `actionban`: command executed when banning an IP
- `actionunban`: command executed when unbanning an IP

You can configure Fail2ban to call the program from this repository instead
of the default action scripts. With that, Fail2ban will now provide you an
IP host group `{iphostgroup_name}` on your Sophos XG firewall containg all
currently blocked IP hosts.

The IP host group can then be used in firewall rules to block hosts or it can
be used for anything else. Fail2ban and the scripts simply dynamically add or
delete IP hosts to this group, but you can decide how to deal with the group.

**Nothing else than this single group is touched on the Sophos XG.**

When having multiple hosts for blocking, give each one an individual name
for the IP host group and you are done.

## Installation
TBD
### Sophos XG Configuration
- Allow access to the Sophos XG API from the Fail2ban hosts by
  "Backup & Firmware" / "API":
  - Enable "API configuration"
  - Add IP address of th Fail2ban hosts to the allowed IP addresses list

### Fail2ban Configuration



## Configuration
TBD

## Details
The repository has the following major parts:
- `f2b-sophosxg.py`: Python-Program calling the functions from the library
- `f2bsophosxg/`: Python library implementing each Fail2ban actions as described
  above
  - `libf2b.py`: Implementing the Fail2ban actions
  - `libsophosxg.py`: Building XML requests for the Sophos XG API and
    implementing the API calls and the error handling
  - `libutil.py`: Some small helper functions (checking for valid IP,
    load config, etc.)
- `action.d/`: Fail2ban configuration template for
  `/etc/fail2ban/config/action.d/`

The library `libf2b.py `implements each of the Fail2ban actions described
above. Basically it calles functions from `libsohposxg.py`. It creates the XML
requests for the desired Fail2ban actions and sends it to the Sophos XG API.
For example, API calls are done to:
- add IP host
- add IP host group
- add IP host to IP host group
- delete IP host from IP host group
- delete IP host
- delete IP host group

To reach that, some characteristics of the Sophos XG API have to be considered:
- IP hosts can only be deleted when they aren't member of any IP host group
- The exsistence of the IP host group is necessary to add an IP host to it
- No IP host group will be deleted by the library, since it may be used in
  firewall rules
