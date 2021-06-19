# Fail2ban Sophos XG API
Access the Sophos XG API from Fail2ban to block hosts on perimeter firewall

This repository contains a program and a small python library to call the
Sophos XG API from Fail2ban. With this, you can enable Fail2ban to block
malicious hosts not on the internal host firewall, but on the perimeter
firewall.

## Usage
```shell
$ python3 f2b-sophosxg.py --help
usage: f2b-sophosxg.py [-h] [--ip IP] [--configfile CONFIGFILE]
                       {start,stop,check,flush,ban,unban}

f2b-sophosxg: Access Sophos XG API from Fail2ban to block hosts on perimeter
firewall.

positional arguments:
  {start,stop,check,flush,ban,unban}
                        Action to execute

optional arguments:
  -h, --help            show this help message and exit
  --ip IP               IPv4 address, required for action 'ban' or 'unban'
  --configfile CONFIGFILE
                        Configuration file path
```

## Overview
You can configure Fail2ban to call the program from this repository instead
of the default action scripts. With that, Fail2ban will now provide you an
IP host group `{iphostgroup_name}` on your Sophos XG firewall containg all
currently blocked IP hosts.

The IP host group can then be used in firewall rules to block hosts or it can
be used for anything else. Fail2ban and this program simply dynamically add or
delete IP hosts to this group, but you can decide how to deal with the group.

**Nothing else except this single IP host group is touched on the Sophos XG.**

When having multiple hosts using Fail2ban, give each one an individual name
for the IP host group and you are done.

## Installation
### Requirements
- These packages have to be installed on the system:
  - python3
  - fail2ban
  ```bash
  $ sudo apt-get install python3 fail2ban
  ```

### Installation
Installation of the program `f2b-sophosxg.py` is done by copying as follows:
```
f2b-sophosxg.py           ->  /usr/local/sbin/f2b-sophosxg.py
f2bsophosxg/*             ->  /usr/local/lib/f2bsophosxg/
config.json               ->  /usr/local/etc/f2bsophosxg/config.json
action.d/sophosxg.conf    ->  /etc/fail2ban/action.d/sophosxg.conf
```

:warning: Ensure `chmod 0600` is set for
`/usr/local/etc/f2bsophosxg/config.json` as it contains credentials!

## Configuration
Configuration is done in three steps:
- Create API user on Sophos XG
- Configure `config.json` with a valid configuration to access Sophos XG API
- Configure Fail2ban to use `sophosxg.conf` as actions

### Sophos XG Configuration
- Allow access to the Sophos XG API from the Fail2ban hosts:
  - "Backup & Firmware" / "API":
  - Enable "API configuration"
  - Add IP address of the Fail2ban hosts to the allowed IP addresses list
- Create an access profile for Fail2ban API users:
  - "Profiles" / "Devices access"
  - Add new profile `f2b-api-access`:
    - "Objects" = "Read-write"
    - "Network" = "Read-write"
    - Others = "None"
- Create an user for each Fail2ban host:
  - "Authentication" / "Users"
  - Add new user:
    - Set "Username" `apiuser` and "Name"
    - "User type": "Administrator" (Don't worry, thus we set the Profile!)
    - "Profile": "`f2b-api-access`"
    - Set "Password" `password`

### `f2b-sophosxg.py` Configuration
Set credentials for the Sophos XG API in
`/usr/local/etc/f2b-sophosxg/config.json` as follows:
```json
{
  "url":"https://<IP/Domain:Port>/webconsole/APIController",
  "verifySslCertificate":true,
  "user":"apiuser",
  "pass":"password",
  "iphost_prefix":"f2b_",
  "iphostgroup_name":"f2b_blockings"
}
```

If you have multiple hosts, you can set the `iphost_prefix` and the
`iphostgroup_name` as follows:
```json
{
  ...
  "iphost_prefix":"f2b_hostname1_",
  "iphostgroup_name":"f2b_hostname1_blockings"
}
```

:warning: Do not use the same names for more than one host, as flush actions
from one Fail2ban host will affect the blockings of the other hosts!

### Fail2ban Configuration
- Set `banaction = sophosxg` either in your jail or for all jails:
  ```bash
  # /etc/fail2ban/jail.d/defaults-debian.conf 
  [sshd]
  enabled = true

  banaction = sophosxg
  ```

## Details
### Overview
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

### Structure of the repository
The repository has the following major parts:
- `f2b-sophosxg.py`: Main python program calling the functions from the library
- `f2bsophosxg/`: Python library implementing each Fail2ban actions as described
  above
  - `libf2b.py`: Defining a base class for generic Fail2ban actions
  - `libf2bsophosxg.py`: Derived class from the base class for Sophos XG
      specific Fail2ban actions
  - `libsophosxg.py`: A dedicated class implementing Sophos XG API calls and
      the error handling
- `action.d/`: Fail2ban configuration template for
  `/etc/fail2ban/config/action.d/`

### Functionality of the program and the libraries
The library `libf2b.py `implements an abstract base class with each of the
generic Fail2ban actions described above. Basically this class can be used
to derive a specific class for each API / firewall / etc. that should be
available to Fail2ban. This is called `libf2bsophosxg.py` here for an
implementation of the Sophos XG firewall API. The class uses
`libsophosxg.py` to create the XML requests for the desired Fail2ban actions
and sending them to the Sophos XG API.
For example, API calls are done to:
- add IP host
- add IP host group
- add IP host to IP host group
- delete IP host from IP host group
- delete IP host
- delete IP host group

### Characteristics
To reach that, some characteristics of the Sophos XG API have to be considered:
- IP hosts can only be deleted when they aren't member of any IP host group
- The exsistence of the IP host group is necessary to add an IP host to it
- No IP host group will be deleted by the library, since it may be used in
  firewall rules
