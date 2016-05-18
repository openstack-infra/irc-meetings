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

import datetime
import os
import pytz
import sys
import yaml

EAVESDROP = 'eavesdrop.openstack.org'
PATH = './meetings/'
WEEKDAYS = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6}
WEEK_COUNTS = {'weekly': 2, 'biweekly-even': 1, 'biweekly-odd': 1}
CHANNELS = ['openstack-meeting', 'openstack-meeting-alt',
            'openstack-meeting-3', 'openstack-meeting-4']
# For now don't include -cp meetings as that not a completely general meeting
# location
# CHANNELS.append('openstack-meeting-cp')

now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
meetings = []
if not os.path.isdir(PATH):
    sys.exit(1)

for root, dirs, files in os.walk(PATH):
    for f in files:
        if not os.path.splitext(f)[1] == '.yaml':
            continue

        fname = os.path.join(root, f)
        with open(fname, 'r') as f_obj:
            obj = yaml.safe_load(f_obj)
            obj['filefrom'] = fname
            meetings.append(obj)

counts = {}
for hour in range(24):
    counts[hour] = {}
    for day in WEEKDAYS:
        counts[hour][day] = []

for m in meetings:
    if 'meeting_id' in m:
        meeting_id = ('http://%s/meetings/%s/%04d/?C=N;O=D' %
                      (EAVESDROP, m['meeting_id'].replace('-', '_'),
                       now.year))
    else:
        meeting_id = m['filefrom']

    for s in m['schedule']:
        try:
            day = s['day']
            time = s['time']
            week_count = WEEK_COUNTS[s['frequency']]
        except KeyError:
            print("KeyError in here somewhere!")
            print("meeting  = %s" % (m))
            print("schedule = %s" % (s))
            print("\n")
            continue

        hour = int(time[:-2])
        mins = int(time[-2:])
        duration = int(s.get('duration', 60))

        if s['irc'] not in CHANNELS:
            # Handy for debugging
            # print("%s: %s" % (m['filefrom'], s))
            continue

        # This is a little hacky way to handle alternating meetings.
        # The "counts" gathered are per fortnight so a weekkly meeting takes up
        # 2 slots, and an alternating (biweekly-*) only one.
        # This means that a "full slot" will be one that has 8 scheduled
        # meetings
        for i in range(week_count):
            counts[hour][day].append(meeting_id)
            # Check for and record meetings that cross multiple hours (This
            # assumes that we don't have any meetings that are longer than
            # 60mins)
            if (mins + duration) > 60:
                counts[(hour+1) % 24][day].append(meeting_id)

for day in sorted(WEEKDAYS, key=lambda key: WEEKDAYS[key]):
    for hour in range(24):
        if len(counts[hour][day]) >= 8:
            print('%-10s %02d' % (day, hour))
            # Handy for debugging
            # print("\t%s" % ("\n\t".join(sorted(counts[hour][day]))))
            meeting_ids = sorted(set(counts[hour][day]))
            for meeting_id in meeting_ids:
                print('%14s%s' % ('', meeting_id))

# FIXME: There is probably a nice CSV library for some of this guff :(
out_fname = os.path.expanduser(os.path.join('~', 'tmp', 'busy.csv'))
with open(out_fname, 'w+') as out:
    print("Hour,Mon,Tue,Wed,Thu,Fri,Sat,Sun", file=out)
    for hour in range(24):
        row = [str(hour)]
        for day in sorted(WEEKDAYS, key=lambda key: WEEKDAYS[key]):
            row.append(str(len(counts[hour][day])))
        print(','.join(row), file=out)
