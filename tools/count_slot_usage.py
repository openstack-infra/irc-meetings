#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import print_function

import calendar
import csv
import datetime
import locale
import os
import sys
import tempfile

import pytz
import yaml

# Ensure calendar.day_name gives us Monday, Tuesday, ...
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


EAVESDROP = 'eavesdrop.openstack.org'
PATH = os.path.abspath('./meetings/')
# Create day_name to day_number dict { 'Monday': 0, ... }
WEEKDAYS = { calendar.day_name[x]: x for x in range(0, 7) }
WEEK_COUNTS = {'weekly': 2, 'biweekly-even': 1, 'biweekly-odd': 1}
CHANNELS = ['openstack-meeting', 'openstack-meeting-alt',
            'openstack-meeting-3', 'openstack-meeting-4']
# For now don't include -cp meetings as that not a completely general meeting
# location
# CHANNELS.append('openstack-meeting-cp')

def main():
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    meetings = []
    if not os.path.isdir(PATH):
        sys.exit("Unable to find directory: {}".format(PATH))

    for dirpath, dirnames, filenames in os.walk(PATH):
        for file_name in filenames:
            if not file_name.endswith('.yaml'):
                continue
            full_path = os.path.join(dirpath, file_name)
            with open(full_path, 'r') as f_obj:
                obj = yaml.safe_load(f_obj)
                obj['filefrom'] = full_path
                meetings.append(obj)

    counts = {}
    for hour in range(24):
        counts[hour] = {}
        for day in WEEKDAYS:
            counts[hour][day] = []

    for meeting in meetings:
        if 'meeting_id' in meeting:
            meeting_id = ('http://%s/meetings/%s/%04d/?C=N;O=D' %
                          (EAVESDROP, meeting['meeting_id'].replace('-', '_'),
                           now.year))
        else:
            meeting_id = meeting['filefrom']

        for schedule in meeting['schedule']:
            try:
                day = schedule['day']
                time = schedule['time']
                frequency = schedule['frequency']
                week_count = WEEK_COUNTS[frequency]
                irc = schedule['irc']
            except KeyError:
                print("KeyError in here somewhere!")
                print("meeting  = %s" % (meeting))
                print("schedule = %s" % (schedule))
                print("\n")
                continue

            hour = int(time[:-2])
            mins = int(time[-2:])
            duration = int(schedule.get('duration', 60))

            if irc not in CHANNELS:
                # Handy for debugging
                # print("%s: %s" % (meeting['filefrom'], schedule))
                continue

            # This is a little hacky way to handle alternating meetings.  The
            # "counts" gathered are per fortnight so a weekly meeting takes up
            # 2 slots, and an alternating (biweekly-*) only one.  This means
            # that a "full slot" will be one that has 8 (2 * number of meeting
            # channels) scheduled meetings
            meeting_info = "{:<13} - {:<21} - {}".format(frequency, irc, meeting_id)
            for i in range(week_count):
                counts[hour][day].append(meeting_info)
                # Check for and record meetings that cross multiple hours (This
                # assumes that we don't have any meetings that are longer than
                # 60mins)
                if (mins + duration) > 60:
                    counts[(hour+1) % 24][day].append(meeting_info)

    print("Day\tUTC Hour\tMeeting time slots which are full or almost full")
    full_time_slot = (2 * len(CHANNELS)) - 1
    for day in sorted(WEEKDAYS, key=lambda key: WEEKDAYS[key]):
        for hour in range(24):
            if len(counts[hour][day]) >= full_time_slot:
                print('%-10s %02d' % (day, hour))
                # Handy for debugging
                # print("\t%s" % ("\n\t".join(sorted(counts[hour][day]))))
                meeting_ids = sorted(set(counts[hour][day]))
                for meeting_id in meeting_ids:
                    print('%14s%s' % ('', meeting_id))

#    # FIXME: There is probably a nice CSV library for some of this guff :(
#
#    BUG: Assumes there is a ~/tmp/ directory.
#    out_fname = os.path.expanduser(os.path.join('~', 'tmp', 'busy.csv'))
#    with open(out_fname, 'w+') as out:
#        print("Hour,Mon,Tue,Wed,Thu,Fri,Sat,Sun", file=out)
#        for hour in range(24):
#            row = [str(hour)]
#            for day in sorted(WEEKDAYS, key=lambda key: WEEKDAYS[key]):
#                row.append(str(len(counts[hour][day])))
#            print(','.join(row), file=out)


if '__main__' == __name__:
    sys.exit(main())
