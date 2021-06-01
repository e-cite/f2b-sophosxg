from os import sys
from f2bsophosxg.libutil import (
  readConfig,
  isConfigValid
)

# Globally load the config
global config
config = readConfig('config.json')
if not isConfigValid(config):
  config = None
  sys.exit(1)
