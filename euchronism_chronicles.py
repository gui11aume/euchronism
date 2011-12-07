# -*- coding: utf-8 -*-

import os
import re
import cgi
import datetime
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


class ChronicleForm(webapp.RequestHandler):
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
               app_admin.chronicle_key(),
               user)

         very_first_user_login = data.count() == 0
         if very_first_user_login:
            # Grab a new instance of user data.
            user_data = app_admin.EuchronismData(app_admin.chronicle_key())
            user_data.user = user
            user_data.put()
         else:
            user_data = data[0]

         dot = os.path.dirname(__file__)

         template_path = os.path.join(dot, 'euchronism_template.html')
         template_values = {
            'page_title': 'Euchronism (%s)' % user.email(),
            'page_content': open(
                os.path.join(dot, 'content', 'chronicle_content.html')
            ).read(),
            'logout_url': users.create_logout_url("/"),
         }

         # ... and send!
         self.response.out.write(
               template.render(template_path, template_values)
         )



class ChroniclePost(webapp.RequestHandler):
   """Handle chronicle post."""

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
               app_admin.chronicle_key(),
               user)

      date_string = self.request.get('date')
      chronicle = self.request.get('chronicle')

      try:
         # Try to interpret user-input date.
         datetime.datetime.strptime(date_string, '%m/%d/%Y')
         specified_date_is_valid = True
         content_file = 'itworked_content.html'
      except Exception:
         # Cannot make a date out of user input: good-bye!
         specified_date_is_valid = False
         content_file = 'itdidnotwork_content.html'


      if specified_date_is_valid:
         user_data = data[0]
         chronicle_docs = json.loads(user_data.chronicles or '{}')

         if date_string in chronicle_docs.keys():
            chronicle_docs[date_string] += \
               app_admin.CHRONICLE_SEPARATOR + chronicle
         else:
            chronicle_docs[date_string] = chronicle

         user_data.chronicles = json.dumps(chronicle_docs)
         user_data.put()

      dot = os.path.dirname(__file__)

      template_path = os.path.join(dot, 'euchronism_template.html')
      template_values = {
         'page_title': 'Chronicle saved (%s)' % user.email(),
         'page_content': open(
             os.path.join(dot, 'content', content_file)
         ).read(),
         'logout_url': users.create_logout_url("/"),
      }

      self.response.out.write(
            template.render(template_path, template_values)
      )


application = webapp.WSGIApplication([
  ('/', ChronicleForm),
  ('/chroniclepost', ChroniclePost),
], debug=True)


def main():
   run_wsgi_app(application)


if __name__ == '__main__':
    main()
