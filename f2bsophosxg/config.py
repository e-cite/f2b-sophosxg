from os import sys
from f2bsophosxg.libutil import (
  readConfig,
  isConfigValid
)

# Globally load the config
global config
file = '/usr/local/etc/f2b-sophosxg/config.json'
try:
  config = readConfig(file)
except FileNotFoundError:
  print("Configuration file",file,"not found.")
  sys.exit(1)

if not isConfigValid(config):
  config = None
  sys.exit(1)
