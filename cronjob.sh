#!/bin/bash
domain="$(hostname -f)"
home=/var/decarbonate
while read cmd args; do
    case "$cmd" in
        domain|token|rcpt|home|name)
            declare $cmd="$args"
            ;;
        channel)
            read chanid channel <<<"$args"
            out="$(mktemp)"
            "$home/digest.py" -i $chanid $token >"$out"
            if [[ -s "$out" ]]; then
                mail -t <<EOF
From: slack+$token.$chanid@$domain
To: $rcpt
Subject: Slack digest of $channel on $name

$(cat $out)
EOF
            fi
            rm "$out"
    esac
done < /etc/bubbles
