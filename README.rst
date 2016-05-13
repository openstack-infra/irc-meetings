==================
OpenStack Meetings
==================

This project aims to provide an easier way to manage OpenStack team meetings.
Currently, each team's meeting time and agenda are listed at:

  https://wiki.openstack.org/wiki/Meetings

This project replaces each meeting with well-defined YAML files.


YAML Meeting File Format
========================

Each meeting consists of:

* ``project``: the name of the project
* ``meeting_id``: the name given to the ``#startmeeting`` meetbot command
* ``agenda_url`` the URL to the page with the agenda for the meeting,
  usually in the wiki
* ``schedule``: a list of schedule each consisting of

  * ``time``: time string in UTC
  * ``day``: the day of week the meeting takes place
  * ``irc``: the irc room in which the meeting is held
  * ``frequency``: frequent occurrence of the meeting
* ``chair``: name of the meeting's chair
* ``description``: a paragraph description about the meeting

The file name should be a lower-cased, hyphenated version of the meeting name,
ending with ``.yaml`` . For example, ``Keystone team meeting`` should be
saved under ``keystone-team-meeting.yaml``.

Example
-------

This is an example of the yaml for the Nova team meeting. The whole file
will be imported into Python as a dictionary.

* The project name is shown below.

  ::

    project:  Nova Team Meeting

* The schedule is a list of dictionaries each consisting of `time` in UTC,
  `day` of the week, the `irc` meeting room, and the `frequency` of the
  meeting. Options for the `frequency` are `weekly`, `biweekly-even`, and
  `biweekly-odd` at the moment.

  ::

    schedule:
        - time:       '1400'
          day:        Thursday
          irc:        openstack-meeting-alt
          frequency:  biweekly-even

        - time:       '2100'
          day:        Thursday
          irc:        openstack-meeting
          frequency:  biweekly-odd

* The chair is just a one liner. The might be left empty if there is not a
  chair.  It's recommended to mention his/her IRC nick.

  ::

    chair:  Russell Bryant (russellb)

* The project description is as follows. Use `>` for paragraphs where new
  lines are folded, or `|` for paragraphs where new lines are preserved.

  ::

    description:  >
        This meeting is a weekly gathering of developers working on OpenStack.
        Compute (Nova). We cover topics such as release planning and status,
        bugs, reviews, and other current topics worthy of real-time discussion.

sample.yaml
-----------

If creating a new yaml meeting file please consider using ``sample.yaml`` and
editing as appropriate.
