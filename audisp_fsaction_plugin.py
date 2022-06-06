#!/usr/bin/env python3
"""
This script is intended as a plugin for audisp:

As root:

  cp audit.rules /etc/audit/rules.d/audit.rules
  cp audisp_fsaction_plugin.conf /etc/audisp/plugins.d/audisp_fsaction_plugin.conf

and adapt both as needed. "fsaction" is used as a key to mark events relevant to
this plugin.

The plugin needs to be owned by root, so do a

  chown root audisp_fsaction_plugin.py

Check /var/log/syslog for errors.


You can also use this directly, e.g. with

  ausearch --start today --raw  | ./audisp_fsaction_plugin.py mylog.log fsaction

This will make the plugin listen to "fsaction" events and write entries into mylog.log
Use '-' as the logfile name to write to stdout.
"""

import sys
from auditd_tools import event_parser

if len(sys.argv) < 2:
    print(f'call as {sys.argv[0]} <infile> [key]')
    sys.exit()

# output
logfile_name = sys.argv[1]

filters = dict(action=event_parser.file_actions)

# key
if len(sys.argv) == 3:
    filters['key'] = sys.argv[2]

parser = event_parser.AuditdEventParser()

logfile = sys.stdout if logfile_name == '-' else open(logfile_name, 'a')
for line in sys.stdin:
    for event in parser.parseline(line, **filters):
        if event['filepath']:
            logfile.write(f"{event['action']:30}: {event['filepath']}\n")
            logfile.flush()
