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

import argparse
import calendar
import csv
import datetime
import locale
import os
import sys

import pytz
import yaml

# Ensure calendar.day_name gives us Monday, Tuesday, ...
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
EAVESDROP = 'eavesdrop.openstack.org'
MEETINGS_PATH = os.path.join(BASE_DIR, 'meetings')
# Create day_name to day_number dict {'Monday': 0, ...}
WEEKDAYS = {calendar.day_name[x]: x for x in range(0, 7)}
WEEK_COUNTS = {'weekly': 2, 'biweekly-even': 1, 'biweekly-odd': 1}
CHANNELS = ['openstack-meeting', 'openstack-meeting-alt',
            'openstack-meeting-3', 'openstack-meeting-4']
# For now don't include -cp meetings as that is restricted to temporary
# cross-project related meetings.
# CHANNELS.append('openstack-meeting-cp')


def main():
    args = parse_args()
    meetings = read_meetings(MEETINGS_PATH)

    meeting_counts = calculate_meeting_counts(meetings)

    print("Day\tUTC Hour")
    available_slots = 2 * len(CHANNELS)
    full_time_slot = available_slots - 1
    for day in sorted(WEEKDAYS, key=lambda key: WEEKDAYS[key]):
        for hour in range(24):
            slot_usage = len(meeting_counts[hour][day])
            if slot_usage >= full_time_slot:
                print('%-10s %02d:00%4s out of %s slots full' % (
                    day, hour, slot_usage, available_slots))
                # Handy for debugging
                # print("\t%s" %
                #       ("\n\t".join(sorted(meeting_counts[hour][day]))))
                meeting_ids = sorted(set(meeting_counts[hour][day]))
                for meeting_id in meeting_ids:
                    print('%4s%s' % ('', meeting_id))

    if args.csv:
        print()
        write_csv_file(args.csv, meeting_counts)


def calculate_meeting_counts(meetings):
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    meeting_counts = {}
    for hour in range(24):
        meeting_counts[hour] = {k: [] for k in WEEKDAYS}

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
            if duration > 60:
                print("Meeting longer than 60 minutes. We don't understand "
                      "that yet")
                print("meeting  = %s" % (meeting))
                print("schedule = %s" % (schedule))
                print("\n")

            if irc not in CHANNELS:
                # Handy for debugging
                # print("%s: %s" % (meeting['filefrom'], schedule))
                continue

            # This is a little hacky way to handle alternating meetings.  The
            # "counts" gathered are per fortnight so a weekly meeting takes up
            # 2 slots, and an alternating (biweekly-*) only one.  This means
            # that a "full slot" will be one that has 8 (2 * number of meeting
            # channels) scheduled meetings
            meeting_info = (
                "{:<13} - {} - {:<21} - {}".format(frequency, time, irc,
                                                   meeting_id))
            for i in range(week_count):
                meeting_counts[hour][day].append(meeting_info)
                # Check for and record meetings that cross multiple hours (This
                # assumes that we don't have any meetings that are longer than
                # 60mins)
                if (mins + duration) > 60:
                    meeting_counts[(hour+1) % 24][day].append(meeting_info)
    return meeting_counts


def write_csv_file(filename, meeting_counts):
    filename = os.path.abspath(os.path.expanduser(filename))
    with open(filename, 'w') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(["Hour", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat",
                         "Sun"])
        for hour in range(24):
            row = [str(hour)]
            for day in sorted(WEEKDAYS, key=lambda key: WEEKDAYS[key]):
                row.append(str(len(meeting_counts[hour][day])))
            writer.writerow(row)
    print("Created CSV file of meeting slot usage at: {}".format(filename))


def read_meetings(meeting_directory):
    meetings = []
    if not os.path.isdir(meeting_directory):
        sys.exit("Unable to find meeting directory: {}".format(
            meeting_directory))

    for dirpath, dirnames, filenames in os.walk(meeting_directory):
        for file_name in filenames:
            if not file_name.endswith('.yaml'):
                continue
            full_path = os.path.join(dirpath, file_name)
            with open(full_path, 'r') as f_obj:
                obj = yaml.safe_load(f_obj)
                obj['filefrom'] = full_path
                meetings.append(obj)
    return meetings


def parse_args():
    parser = argparse.ArgumentParser(
        description='Check meeting count time usage')
    parser.add_argument(
        '--csv', metavar='FILE_NAME',
        help='If specified, write counts to the specified CSV file')

    args = parser.parse_args()
    return args


if '__main__' == __name__:
    sys.exit(main())
