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

      today = datetime.datetime.today().strftime('%Y/%m/%d')

      # Get all users data.
      data = app_admin.EuchronismData.gql(
            'WHERE ANCESTOR IS :1', app_admin.lightray_key()
      )

      for user_data in data:

         # Embed in a try. Send a mail to admin in case of failure.
         try:
            lightrays = json.loads(user_data.lightrays or '{}')
            if today in lightrays.keys():
               todays_lightray = lightrays.pop(today)
   
               msg = mail.EmailMessage()
               msg.initialize(
                  to = user_data.user.email(),
                  sender = app_admin.ADMAIL,
                  subject = 'Your light ray has returned'
                  body = todays_lightray
               )
               msg.send()
   
               user_data.lightrays = json.dumps(lightrays)
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
