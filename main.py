#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import PushYourLuckApi

from models import User


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        games = Game.query(Game.game_over == False)
        for game in games:
            user = User.query(ndb.AND(
                                User.key == game.user,
                                User.email != None)).get()
            for user in users:
                subject = 'This is a reminder!'
                body = 'Hello {}, we have an unfinished business. Do you wanna push your luck in game {}?'.format(
                                                                    user.name,
                                                                    game.key)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)


class UpdateAverageAttemtps(webapp2.RequestHandler):
    def post(self):
        """Update average attempts in memcache."""
        PushYourLuckApi._cache_average_attempts()
        self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_attempts', UpdateAverageAttemtps),
], debug=True)
