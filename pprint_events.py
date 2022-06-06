#!/usr/bin/env python3
"""
Print events using pythons pprint.

Provide a filename (or '-' for stdin) as an argument. No argument will default to 'test.log'

Example use:

ausearch --start today --raw  | ./pprint_events.py -

"""
import sys
from pprint import pprint

from auditd_tools import event_parser

p = event_parser.AuditdEventParser()
filename = sys.argv[1] if len(sys.argv) > 1 else 'test.log'
fp = sys.stdin if filename == '-' else open(filename)

for line in fp:
    for e in p.parseline(line):
        pprint(e)
        print('\n----\n')
