#!/usr/bin/env python3
import argparse
import sys
import slacker
import datetime
import pytz
import textwrap
import re
from functools import lru_cache

parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--delta',
    type=int,
    default=1440,
    help="How much time (in minutes) has it been since the last digest? Default is 1440 (24 hours)."
)
parser.add_argument(
    '-c', '--channel',
    type=str,
    default='general',
    help="Channel to digest, default is general"
)
parser.add_argument(
    '-i', '--chanid',
    type=str,
    help="Channel ID to digest, overrides channel option"
)
parser.add_argument(
    '-w', '--wrap',
    type=int,
    default=72,
    help="How long should the lines be? Default is 72 columns."
)
parser.add_argument(
    '-l', '--list',
    action="store_true",
    help="List channels and exit"
)
parser.add_argument(
    '-z', '--timezone',
    type=pytz.timezone,
    default=datetime.datetime.now().astimezone().tzinfo,
    help="Timezone for Messages (e.g., US/Mountain), default is to use local time."
)
parser.add_argument(
    '-f', '--filthy',
    action="store_true",
    help="Don't strip out worthless messages, crazy emojis, etc."
)
parser.add_argument(
    'token',
    type=str,
    help="Slack API Token"
)
args = parser.parse_args()

slack = slacker.Slacker(args.token)
channels = (slack.channels.list().body['channels']
              + slack.groups.list().body['groups'])

if args.list:
    for c in channels:
        print(c['id'], c['name'])
    sys.exit(0)
if args.chanid:
    chan_id = args.chanid
else:
    for c in channels:
        if c['name'] == args.channel:
            chan_id = c['id']
            break
    else:
        print("No such channel: {}".format(args.channel), file=sys.stderr)
        sys.exit(1)

histr = {'C': slack.channels.history, 'G': slack.groups.history}[chan_id[0]](
    chan_id,
    oldest=
        (datetime.datetime.now()
       - datetime.timedelta(minutes=args.delta)).timestamp(),
    count=1000
)

lastuser = ''
lasttime = datetime.datetime.fromtimestamp(0)

@lru_cache(maxsize=250)
def get_user_name(user_id):
    return slack.users.info(user_id).body['user']['name']

emoji_p = re.compile(r' *:[a-z0-9_+]+: *')

worthless_messages = [
    re.compile(text, re.I)
    for text in [
        'awesome!*',
        '!+',
        '(hi|hey|hello)( (folks|everyone))?!*',
        'thanks!*',
        'thank you!*',
    ]
]

smileys = [
    (':stuck_out_tongue:', ':P'),
    (':grinning:', ':D'),
    (':smile:', ':)'),
    (':smiley:', ':)'),
    (':wink:', ';)'),
    (':unamused:', ':/'),
    (':disappointed:', ':('),
    (':cry:', ':('),
    (':scream:', ':O'),
]

at_mention_p = re.compile('<@([A-Z0-9]+)>')

for msg in reversed(histr.body['messages']):
    if not args.filthy:
        if msg.get('subtype') in ('channel_join', 'group_join', 'bot_add'):
            continue
        for orig, repl in smileys:
            msg['text'] = msg['text'].replace(orig, repl)
        msg['text'] = emoji_p.sub(' ', msg['text']).strip()
        if not msg['text']:
            continue
        if any(p.fullmatch(msg['text']) for p in worthless_messages):
            continue
    if 'username' in msg.keys():
        user_name = msg['username']
    elif 'user' in msg.keys():
        user_name = get_user_name(msg['user'])
    else:
        user_name = 'Unknown'
    msg['text'] = at_mention_p.sub(lambda m: '@' + get_user_name(m.group(1)), msg['text'])
    time = datetime.datetime.fromtimestamp(float(msg.get('ts')), tz=args.timezone)
    if lastuser == user_name and time < lasttime + datetime.timedelta(minutes=6):
        print("> ")
    else:
        if lastuser:
            print()
        print("On {}, {} wrote:".format(
            time.strftime('%Y-%m-%d at %H:%M'),
            user_name)
        )
    print('> ' + '\n> '.join(textwrap.wrap(msg.get('text'), width=args.wrap - 2)))
    lastuser = user_name
    lasttime = time
