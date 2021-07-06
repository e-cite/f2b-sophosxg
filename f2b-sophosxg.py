import json
import sys
import argparse
sys.path.append("/usr/local/lib")
import f2bsophosxg.libf2bsophosxg

# Open and read the config file
# Arguments: Filename
# Returns: config-dict
def readConfig(file):
  with open(file, 'r') as f:
    config = json.load(f)
  return config

# Create argument parser and set description
parser = argparse.ArgumentParser(
  description='f2b-sophosxg: Access Sophos XG API from Fail2ban to block hosts\
  on perimeter firewall.'
)
# Positional, required argument
parser.add_argument('action', help='Action to execute', choices=(
  'start',
  'stop',
  'check',
  'flush',
  'ban',
  'unban')
)
# Optional argument is required when 'ban' or 'unban' is set
parser.add_argument('--ip',
  help='IPv4 address, required for action \'ban\' or \'unban\'',
  required='ban' in sys.argv
)
# Optional argument
parser.add_argument('--configfile',
  help='Configuration file path'
)

# Parse the input arguments
args = parser.parse_args()

# Use configfile argument if present, or default config file
if args.configfile:
  configfile = args.configfile
else:
  configfile = '/usr/local/etc/f2b-sophosxg/config.json'

config = readConfig(configfile)

# Instantiate object
f2b = f2bsophosxg.libf2bsophosxg.f2bsophosxg(config)

# Set default return code
ret = 0

# Execute f2b methods depending on choice
if args.action == 'start':
  ret = f2b.start()
elif args.action == 'stop':
  ret = f2b.stop()
elif args.action == 'check':
  ret = f2b.check()
elif args.action == 'flush':
  ret = f2b.flush()
elif args.action == 'ban':
  ret = f2b.ban(args.ip)
elif args.action == 'unban':
  ret = f2b.unban(args.ip)

sys.exit(ret)
