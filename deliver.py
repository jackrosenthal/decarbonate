#!/usr/bin/env python3
import sys
import email
import slacker
import re

def get_plaintext_body(message):
    body = ""

    if message.is_multipart():
        for part in message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)
                break
    else:
        body = message.get_payload(decode=True)

    if isinstance(body, bytes):
        body = body.decode('utf-8')

    return body

msg = email.message_from_file(sys.stdin)
m = re.match(r"slack+([A-Za-z0-9-]+).([A-Z0-9]+)@", msg["To"])
token, chanid = m.groups()
slack = slacker.Slacker(token)
slacker.chat.post_message(
    channel=chanid,
    text="```{}```".format(get_plaintext_body(msg)),
    as_user=True
)
