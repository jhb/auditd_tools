#!/usr/bin/env python3
"""
Print events as a log of actions in the filesystem

Provide a filename (or '-' for stdin) as an argument. No argument will default to 'test.log'

You can optionally provide a filter key as the second argument

Example use:

ausearch --start today --raw  | ./fileaction_events.py - fsaction

"""

import sys
import event_parser

if len(sys.argv) < 2:
    print(f'call as {sys.argv[0]} <infile> [key]')
    sys.exit()

# input
in_file_name = sys.argv[1]
fp = sys.stdin if in_file_name == '-' else open(in_file_name)

filters = dict(action=event_parser.file_actions)

# key
if len(sys.argv) == 3:
    filters['key'] = sys.argv[2]

parser = event_parser.AuditdEventParser()

for line in fp:
    for event in parser.parseline(line, **filters):
        if event['filepath']:
            print(f"{event['action']:30}: {event['filepath']}")
