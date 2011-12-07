# -*- coding: utf-8 -*-

import os
import datetime
try:
   import json
except ImportError:
   import simplejson as json

import app_admin

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import mail
from google.appengine.ext.webapp.util import run_wsgi_app


class Despatcher(webapp.RequestHandler):
   """Called by the cron scheduler."""

   def get(self):

      today = datetime.datetime.today().strftime('%m/%d/%Y')

      # Get all users data.
      data = app_admin.EuchronismData.gql(
            'WHERE ANCESTOR IS :1', app_admin.chronicle_key()
      )

      for user_data in data:

         # Embed in a try. Send a mail to admin in case of failure.
         try:
            chronicles = json.loads(user_data.chronicles or '{}')
            if today in chronicles.keys():
               todays_chronicle = chronicles.pop(today)
   
               msg = mail.EmailMessage()
               msg.initialize(
                  to = user_data.user.email(),
                  sender = app_admin.ADMAIL,
                  subject = 'Chronicle',
                  body = todays_chronicle
               )
               msg.send()
   
               user_data.chronicles = json.dumps(chronicles)
               user_data.put()

         except Exception:
            app_admin.mail_admin(app_admin.ADMAIL)


application = webapp.WSGIApplication([
  ("/send", Despatcher),
], debug=True)

def main():
   run_wsgi_app(application)

if __name__ == '__main__':
    main()
