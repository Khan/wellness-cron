# -*- coding: utf-8 -*-
import csv
import json
import logging
import random
import re
import urllib2

from google.appengine.api import memcache
import webapp2

import alertlib

_DEFAULT_CHANNEL = "#wellness"
_CULTURE_MESSAGES_CSV_URL = "https://docs.google.com/spreadsheets/d/1X3V3kSvqlOX4rj6w1NDagkXNrahRxb0iBSWmSne78vk/pub?gid=0&single=true&output=csv"

_RESPOND_REGEXP = re.compile(r'fitness us$')


def _get_cached_culture_csv():
    """Retrieve the exported CSV from Google Docs, cached for up to 5 min."""
    key = 'cultural_learnings_of_cow_for_make_benefit_glorious_devteam_of_khan'
    cached_data = memcache.get(key)
    if cached_data is None:
        fresh_data = urllib2.urlopen(_CULTURE_MESSAGES_CSV_URL).read()
        if not memcache.set(key=key, value=fresh_data, time=300):
            logging.error('memcache set failed!')
        return fresh_data
    else:
        return cached_data


def _get_culture():
    lines = _get_cached_culture_csv().splitlines()[1:]
    msgs = list(csv.reader(lines))
    message = random.choice(msgs)[0]
    moo = 'M' + 'o' * random.randrange(2, 10) + '.'
    return "%s  %s" % (message, moo)


class Culture(webapp2.RequestHandler):
    def get(self):
        """Invoked by cron."""
        alertlib.Alert(_get_culture()).send_to_slack(
            _DEFAULT_CHANNEL, sender="Fitbot", icon_emoji=":robot_face:")

    def post(self):
        """Hit by the culture cow outgoing webhook in Slack.

        In this case, we can just return our reply in HTTP and be done.
        """
        if _RESPOND_REGEXP.search(self.request.get("text")) is not None:
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps({'text': _get_culture()}))


app = webapp2.WSGIApplication([
    ('/culture', Culture),
])
