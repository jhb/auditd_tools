import datetime
import warnings
from typing import Dict, List

import auparse

warnings.filterwarnings("ignore", category=DeprecationWarning)

# describe here which file actions there are, and in which record, defined by
# its item number the corresponding filepath is found in the 'name attribute'
action_item_map = {('deleted', 'opened-file'):      1,
                   ('changed-file-attributes-of',): 0}

# all the keys of the action_item_map flattened out.
file_actions = [a for keys in action_item_map for a in keys]


def handler(ap: auparse.AuParser, cb_event_type, parser):
    """The handler for ap.add_callback needs to be a function. So be it."""
    if cb_event_type == auparse.AUPARSE_CB_EVENT_READY:
        parser.parse_event(ap)


class AuditdEventParser:

    def __init__(self):
        self.ap = auparse.AuParser(auparse.AUSOURCE_FEED, None)
        self.ap.add_callback(handler, self)
        self.finished_events = []  # this may contain parsed events

    def parseline(self, line: str, **filters) -> List[Dict]:
        """Main method to feed the parser. Will call the handler, which will call _parse_event

        - line: a line from auditd
        - **filters: attributes to filter for, e.g. key=fsaction
        """
        self.ap.feed(line)  # calls _parse_event in return
        if fe := self.finished_events:
            self.finished_events = []
            out = []
            for e in fe:  # go through the events
                # check if the filter criteria are met
                do_return = all(e[key] in values for key, values in filters.items())
                if do_return:
                    out.append(e)
            return out
        else:
            return []

    def parse_event(self, ap: auparse.AuParser) -> None:
        """The actual parse method, called by the handler. Returns nothing, but puts parsed events
        into self.finished_events.
        """

        while True:  # events

            # basic setup of the event
            auevent = ap.get_timestamp()
            dt = datetime.datetime.fromtimestamp(auevent.sec + auevent.milli / 1000)
            event = dict(serial=auevent.serial,
                         timestamp=auevent.sec + auevent.milli / 1000,
                         datetime=dt.isoformat(' '),
                         records=[],
                         normalized=dict(),
                         key=None)

            # the ap acts a bit like a database pointer
            ap.first_record()

            while True:  # records

                try:
                    my_type = ap.get_type_name()
                except LookupError:
                    my_type = "UNKNOWN"

                record = dict(_type=my_type,
                              _raw=dict())
                raws = record['_raw']  # save the raw entries here

                while True:  # fields
                    field_name = ap.get_field_name()
                    raw = ap.get_field_str()

                    try:
                        real_path: str = ap.interpret_realpath()  # it still needs to be stored, don't know why
                    except RuntimeError:
                        ...

                    try:
                        escaped = ap.interpret_field()
                    except ValueError:
                        escaped = raw

                    try:
                        escaped = int(escaped)
                    except (TypeError, ValueError):
                        ...

                    if escaped == '(null)':
                        escaped = None

                    record[field_name] = escaped

                    if escaped != raw:  # only save modified raw entries
                        raws[field_name] = raw

                    if field_name == 'key' and escaped is not None:
                        # noinspection PyTypedDict
                        event['key'] = escaped

                    if not ap.next_field():
                        break
                # del record['_raw']
                event['records'].append(record)
                if not ap.next_record():
                    break

            # see https://security-plus-data-science.blogspot.com/2017/06/using-auparse-in-python.html
            normalized = event['normalized']

            if ap.aup_normalize(auparse.NORM_OPT_NO_ATTRS):
                ...
            else:
                try:
                    event_kind = ap.aup_normalize_get_event_kind()
                except RuntimeError:
                    event_kind = ""
                normalized['event_kind'] = event_kind

                if ap.aup_normalize_session():
                    normalized['session'] = ap.interpret_field()

                if ap.aup_normalize_subject_primary():
                    subj = ap.interpret_field()
                    field = ap.get_field_name()
                    if subj == "unset":
                        subj = "system"
                    normalized['subject.primary.field'] = field
                    normalized['subject.primary'] = subj

                if ap.aup_normalize_subject_secondary():
                    subj = ap.interpret_field()
                    field = ap.get_field_name()
                    normalized['subject.secondary.field'] = field
                    normalized['subject.secondary'] = subj

                if ap.aup_normalize_object_primary():
                    field = ap.get_field_name()
                    normalized['object.primary.field'] = field
                    normalized['object.primary'] = ap.interpret_field()

                if ap.aup_normalize_object_secondary():
                    field = ap.get_field_name()
                    normalized['object.secondary.field'] = field
                    normalized['object.secondary'] = ap.interpret_field()

                try:
                    action = ap.aup_normalize_get_action()
                except RuntimeError:
                    action = ""
                normalized['action'] = action

                try:
                    object_kind = ap.aup_normalize_object_kind()
                except RuntimeError:
                    object_kind = ""
                normalized['object_kind'] = object_kind

                try:
                    how = ap.aup_normalize_how()
                except RuntimeError:
                    how = ""
                normalized['how'] = how

            #  The following doesn't add anything we did not already know
            # ap.aup_normalize_subject_first_attribute()
            # subject_attributes = dict()
            # while True:
            #     field = ap.get_field_name()
            #     subject_attributes[field] = ap.interpret_field()
            #     if not ap.aup_normalize_subject_next_attribute(): break
            # normalized['subject_attributes'] = subject_attributes
            #
            # ap.aup_normalize_object_first_attribute()
            # object_attributes = dict()
            # while True:
            #     field = ap.get_field_name()
            #     object_attributes[field] = ap.interpret_field()
            #     if not ap.aup_normalize_object_next_attribute(): break
            # normalized['object_attributes'] = object_attributes

            # guess the filepath
            filepath = ''

            if action := event['normalized'].get('action', None):
                for actions, item_no in action_item_map.items():
                    if action in actions:
                        for record in event['records']:
                            if record.get('item', None) == item_no:
                                filepath = record['name']
            event['filepath'] = filepath
            event['action'] = event['normalized'].get('action', '')

            self.finished_events.append(event)
            if not ap.parse_next_event():
                break
