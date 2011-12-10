# -*- coding: utf-8 -*-

import os
import re
import cgi
import datetime
import random
try:
   import json
except ImportError:
   import simplejson as json
from hashlib import sha1

import app_admin

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


class LightrayForm(webapp.RequestHandler):
   """Handle requests to watch page."""

   def get(self):

      # Get user login status.
      user = users.get_current_user()

      if not user:
         # User is not logged in... Go log in then.
         self.redirect(users.create_login_url(self.request.uri))

      else:
         # User is logged in: welcome to your personal query page!
         data = app_admin.EuchronismData.gql(
               'WHERE ANCESTOR IS :1 AND user = :2',
               app_admin.lightray_key(),
               user)

         very_first_user_login = data.count() == 0
         if very_first_user_login:
            # Grab a new instance of user data.
            user_data = app_admin.EuchronismData(app_admin.lightray_key())
            user_data.user = user
            user_data.put()
         else:
            user_data = data[0]

         dot = os.path.dirname(__file__)

         # Generate the content (not the page).
         content_path = os.path.join(
               dot,
               'content',
               'lightray_content.html'
         )
         content = template.render(
               content_path,
               {'logout_url': users.create_logout_url("/"),}
         )

         template_path = os.path.join(dot, 'euchronism_template.html')
         template_values = {
            'page_title': 'Euchronism (%s)' % user.email(),
            'page_content': content,
         }

         # ... and send!
         self.response.out.write(
               template.render(template_path, template_values)
         )



class LightrayPost(webapp.RequestHandler):
   """Handle lightray post."""

   def get_random_date(self, target_date):
      """Get a random date centered around 'target_date'. The date
      is chosen uniformly with a span equal to the number of days
      between now and 'target_date'."""

      today = datetime.datetime.today()
      days_to_target = (target_date - today).days
      random_delta = random.randint(- days_to_target/2, days_to_target/2)
      return target_date + datetime.timedelta(days = random_delta)


   def post(self):
      # Get user login status
      user = users.get_current_user()

      if not user:
         # User is not logged in -- Why!?!?
         self.redirect('/')
      else:
         # User is logged in.
         data = app_admin.EuchronismData.gql(
               'WHERE ANCESTOR IS :1 AND user = :2',
               app_admin.lightray_key(),
               user
         )

      date_string = self.request.get('date')
      lightray = self.request.get('lightray')

      try:
         # Try to interpret user-input date.
         date = datetime.datetime.strptime(date_string, '%Y/%m/%d')
      except Exception:
         # Cannot make a date out of user input.
         specified_date_is_valid = False
         content_file = 'itdidnotwork_content.html'
      else:
         two_weeks_from_now = datetime.datetime.today() \
               + datetime.timedelta(days=app_admin.MIN_TIME_DELTA)
         if date < two_weeks_from_now:
            # Specified date is too early.
            specified_date_is_valid = False
            content_file = 'itdidnotwork_content.html'
         else:
            specified_date_is_valid = True
            content_file = 'itworked_content.html'


      if specified_date_is_valid:
         # Get a random date.
         random_date = self.get_random_date(date)
         random_date_string = random_date.strftime('%Y/%m/%d')

         # Write the lightray in user data.
         user_data = data[0]
         lightray_docs = json.loads(user_data.lightrays or '{}')

         if random_date_string in lightray_docs.keys():
            lightray_docs[random_date_string] += \
               app_admin.CHRONICLE_SEPARATOR + lightray
         else:
            lightray_docs[random_date_string] = lightray

         user_data.lightrays = json.dumps(lightray_docs)
         user_data.put()

      # Send the answer (success or failure).
      dot = os.path.dirname(__file__)

      template_path = os.path.join(dot, 'euchronism_template.html')
      template_values = {
         'page_title': 'Lightray saved (%s)' % user.email(),
         'page_content': open(
             os.path.join(dot, 'content', content_file)
         ).read(),
         'logout_url': users.create_logout_url("/"),
      }

      self.response.out.write(
            template.render(template_path, template_values)
      )


application = webapp.WSGIApplication([
  ('/', LightrayForm),
  ('/lightraypost', LightrayPost),
], debug=True)


def main():
   run_wsgi_app(application)


if __name__ == '__main__':
    main()
