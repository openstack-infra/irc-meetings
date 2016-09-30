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
import re
import sys

from yaml2ical import meeting

BOOL_STR = {True: 'OK', False: 'Needs Fixing'}


def check_chair(chair):
    if re.search(r',', chair):
        chairs = chair.split(',')
    else:
        chairs = [chair]

    all_good = True
    msg = ''
    for chair in chairs:
        chair = chair.rstrip().lstrip()
        ok = bool(re.match(r"^[\w '.-]+\([\w\d_-]+\)$", chair))
        all_good &= ok
        msg += "\t%s: %s\n" % (chair, BOOL_STR[ok])

    return (all_good, msg)


def main():
    # build option parser:
    description = """
A tool that checks a meeting chair matches the canonical format.
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
    all_good = True
    for m in meetings:
            ok, msg = check_chair(m.chair)
            if not ok:
                all_good = False
                print(m.filefrom)
                print(msg.rstrip())
    return 0 if all_good else 1

if __name__ == '__main__':
    sys.exit(main())
