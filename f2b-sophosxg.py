import sys
import argparse
import f2bsophosxg.libf2b

sys.path.append('f2bsophosxg')

parser = argparse.ArgumentParser(
  description='f2b-sophosxg: Access SophosXG API from fail2ban to block hosts\
  on perimeter firewall.'
)
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

args = parser.parse_args()

# Execute library function depending on choice
if args.action == 'start':
  f2bsophosxg.libf2b.start()
elif args.action == 'stop':
  f2bsophosxg.libf2b.stop()
elif args.action == 'check':
  f2bsophosxg.libf2b.check()
elif args.action == 'flush':
  f2bsophosxg.libf2b.flush()
elif args.action == 'ban':  
  f2bsophosxg.libf2b.ban(args.ip)
elif args.action == 'unban':
  f2bsophosxg.libf2b.unban(args.ip)

sys.exit(0)
