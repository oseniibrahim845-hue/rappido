#!/usr/bin/env python3
"""Tiny local SMTP server for testing: saves every received message to a JSON lines file. Usage: smtp_sink.py <port> <outfile>"""
import sys, json, time
from aiosmtpd.controller import Controller
class H:
    async def handle_DATA(self, server, session, envelope):
        with open(sys.argv[2], "a") as f:
            f.write(json.dumps({"to": envelope.rcpt_tos, "from": envelope.mail_from, "data": envelope.content.decode("utf8", "replace")}) + "\n")
        return "250 OK"
c = Controller(H(), hostname="127.0.0.1", port=int(sys.argv[1])); c.start()
while True: time.sleep(1)
