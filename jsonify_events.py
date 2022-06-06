#!/usr/bin/env python3
"""
Dump events as json, one entry per line (jsonl).

Provide a filename (or '-' for stdin) as an argument. No argument will default to 'test.log'

Example use:

ausearch --start today --raw  | ./jsonify_events.py -

"""

import json
import sys

from auditd_tools import event_parser

p = event_parser.AuditdEventParser()

filename = sys.argv[1] if len(sys.argv) > 1 else 'test.log'
fp = sys.stdin if filename == '-' else open(filename)

for line in fp:
    for e in p.parseline(line):
        print(json.dumps(e))
