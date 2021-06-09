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

f2b = f2bsophosxg.libf2b.fail2ban()

ret = 0

# Execute library function depending on choice
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
