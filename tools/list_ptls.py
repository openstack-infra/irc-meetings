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
import textwrap

import requests
import yaml

PROJECTS_LIST = "http://git.openstack.org/cgit/openstack/governance/plain/reference/projects.yaml"  # noqa


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--project-list',
        default=PROJECTS_LIST,
        help='a URL pointing to a projects.yaml file, defaults to %(default)s',
    )
    parser.add_argument(
        '--msg', '-m',
        default='courtesy ping for',
        help='ping message',
    )
    parser.add_argument(
        'project',
        default=None,
        nargs='*',
        help='projects to include, defaults to all',
    )
    args = parser.parse_args()

    r = requests.get(args.project_list)
    project_data = yaml.load(r.text)

    projects = args.project
    if not projects:
        projects = project_data.keys()

    nick_text = ' '.join([
        project_data[p]['ptl']['irc'] for p in projects
    ])

    print(textwrap.fill(nick_text,
                        initial_indent=args.msg + ' ',
                        subsequent_indent=args.msg + ' ',
                        width=80,
                        ))


if __name__ == '__main__':
    main()
