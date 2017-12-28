Decarbonate
===========

    Bubbleware (n.): Software designed for hipsters designing software.
    Typically delivered "as a service" since hipsters would not know how
    to use it otherwise.

Decarbonate is an open source Slack-to-email digester and gateway. It comes
with two scripts:

1. ``digest.py``, which downloads messages from a certain Slack channel over a
   certain time period and concatenates them to ``stdout``.
2. ``deliver.py``, which accepts an Email on ``stdin`` and posts a message with
   the email body to a certain slack channel.

You will need a slack API token to use these. To get one, set up a new "app" in
Slack, and give it most of the permissions. (what could go wrong?)

I guess how you decide to use these is up to you, but I make a suggestion (how
I use it) how to use it in a nice setup with Postfix and cron.

1. First, place the scripts somewhere on your system (I use
   ``/var/decarbonate/``).
2. Add an alias for the ``slack`` account which pipes to the deliver script::

       slack: "|/var/decarbonate/deliver.py"

   (don't forget to run ``newaliases``)
3. Make sure the recipient delimiter is set to ``+`` in your ``main.cf``::

       recipient_delimiter = +

4. Make a file ``/etc/bubbles`` for the cron job to read. It might look
   something like this::

       rcpt jack@rosenth.al
       name Slack Workspace for teh Hipsters!
       token xoxp-1234567890...
       channel C123458 general
       channel C123456 random

   You can get those channel ID's by running ``digest.py -l YOUR-TOKEN-HERE``.

5. Copy the cron job to ``/etc/cron.daily/`` (or run it daily, however you
   like).
