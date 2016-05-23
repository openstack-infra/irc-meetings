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
from yaml2ical import meeting

channels = set(['openstack-meeting', 'openstack-meeting-alt',
                'openstack-meeting-3', 'openstack-meeting-4',
                'openstack-meeting-cp'])


def main():
    # build option parser:
    description = """
A tool that checks if the IRC channel happens in is capable of running a
fully functional MeetBot.
"""

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description)

    parser.add_argument("-y", "--yamldir",
                        dest="yaml_dir",
                        required=True,
                        help="directory containing YAML to process")

    args = parser.parse_args()
    meetings = meeting.load_meetings(args.yaml_dir)
    for m in meetings:
        for s in m.schedules:
            if s.irc not in channels:
                raise ValueError(("%s: IRC channel: %s not in (%s)") %
                                 (s.filefrom, s.irc,
                                  ', '.join(channels)))

if __name__ == '__main__':
    main()
