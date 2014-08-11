#!/usr/bin/env python3
""" countdown.py
    Stores events and returns the time remaining until those events when asked.

"""

import os
from datetime import datetime, timedelta
from settings import TIMERSFILENAME
import re
import sys

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

events = []
timers_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), TIMERSFILENAME)


def write_timers():
    """Writes currently tracked timers to text file. Called by add_event after each timer is added."""
    try:
        global events
        with open(timers_path, 'w') as file:
            for event in events:
                dt = event[0]
                name = event[1]
                file.write('{};{};{};{};{};{}\n'.format(dt.year, dt.month, dt.day, dt.hour, dt.minute, name))
        print('INFO: Wrote timers.txt')
    except IOError:
        print('PROB: ' + 'Problem writing timers.txt')


def add_timer(match):
    try:
        add_event((datetime.utcnow() + timedelta(days=int(match.group('days')), hours=int(match.group('hours')),
                                                 minutes=int(match.group('minutes')))), match.group('name'))
        return True
    except ValueError:
        return False
    pass


def add_datetime(match):
    try:
        add_event(datetime(int(match.group('year')), int(match.group('month')), int(match.group('day')),
                           int(match.group('hour')), int(match.group('minute'))), match.group('name'))
        return True
    except ValueError:
        return False
    pass


def add_event(adatetime, aname):
    """Appends a (datetime, name) tuple to a list of events then sorts it by datetime order"""
    global events
    if aname == '':
        aname = 'MYSTERY TIMER'
    event = (adatetime, aname)
    events.append(event)
    events = sorted(events, key=lambda list_item: list_item[0])
    write_timers()


def remove_event(rmop_args):
    """Deletes an event at event_index and returns a message to the bot."""
    global events
    try:
        # new
        rmop_args = sorted(set([int(x) for x in rmop_args.split(';')]), reverse=True)
        if max(rmop_args) > len(events) or min(rmop_args) < 1:
            return ['One or more event numbers out of bounds.']
        else:
            reply_lines = []
            for arg in rmop_args:
                removed_event_name = events[arg - 1][1]
                del events[arg - 1]
                write_timers()
                reply_lines.append('Removed event #{}: "{}".'.format(arg, removed_event_name))
        return reply_lines
    except ValueError:
        return ['One or more inputs is not a number.']


def days_hours_minutes(adelta):
    """Returns the value of a time delta as days, hours and minutes."""
    return adelta.days, adelta.seconds // 3600, (adelta.seconds // 60) % 60


# TODO Factor out expiration logic to re-use in remove function
def get_countdown_messages():
    """ Returns a list of messages reporting the time remaining or elapsed relative to each event in the event list.
        Events which have been expired for longer than 45 minutes will be removed from the list on the next .ops call.
        Calls write_timers() if the event list changes.

    """
    global events
    messages = []
    if len(events) == 0:
        messages.append("No upcoming events.")
    else:
        count = 0
        for event in events:
            name = event[1]
            time_delta = event[0] - datetime.utcnow()
            if time_delta.total_seconds() > 0:
                delta = days_hours_minutes(time_delta)
                count += 1
                messages.append(
                    '{0}: {1:3}d {2:2}h {3:2}m until {4} at {5} UTC'.format(count, delta[0], delta[1], delta[2],
                                                                               name,
                                                                               event[0].strftime("%Y-%m-%dT%H:%M")))
            else:
                minutes_elapsed = abs(time_delta.total_seconds()) // 60
                if minutes_elapsed > 30:
                    events = events[1:]
                else:
                    count += 1
                    messages.append('{}:  IT\'S HAPPENING:  \"{}\"'.format(count, name))
    write_timers()
    return messages


def read_timers():
    """Reads saved timers into timers list from text file."""
    global events
    try:
        with open(timers_path, 'r') as file:
            for line in file:
                line = line.split(';')
                timestamp, name = [int(x) for x in line[:-1]], upper_preserving_urls(line[-1].strip())
                event = (datetime(*timestamp), name)
                events.append(event)
        events = sorted(events, key=lambda list_item: list_item[0])
        print('INFO: Read timers.txt')
    except IOError:
        print('PROB: ' + 'Problem reading timers.txt')


def upper_preserving_urls(s):
    """Returns an uppercase version of the given string, but preserves urls which may be case sensitive."""
    urls = re.findall(r'(https?://\S+)', s)
    s = re.sub(r'(https?://\S+)', '{}', s)
    return s.upper().format(*urls)

read_timers()