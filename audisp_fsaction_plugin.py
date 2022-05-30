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

  ausearch --start today --raw  | ./audisp_fsaction_plugin.py fsaction mylog.log

This will make the plugin listen to "fsaction" events and write entries into mylog.log
"""


import os
import sys
import event_parser

if len(sys.argv) > 2:
    filter_key = sys.argv[1]
    logfile_name = sys.argv[2]
else:
    filter_key = 'fsaction'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    logfile_name = os.path.join(dir_path, 'fsaction_plugin.log')
print(logfile_name)
parser = event_parser.AuditdEventParser()

with open(logfile_name, 'a') as logfile:
    for line in sys.stdin:
        for event in parser.parseline(line, key=[filter_key], action=event_parser.file_actions):
            if event['filepath']:
                logfile.write(f"{event['action']:30}: {event['filepath']}\n")
                logfile.flush()
