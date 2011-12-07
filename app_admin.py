# -*- coding: utf-8 -*-
"""
"""

import sys
import traceback

from google.appengine.api import mail
from google.appengine.ext import db

# -------------------------------------------------------------------
ADMAIL = 'euchronism.mailer@gmail.com'
MAX_MAIL_PER_DAY = 100
CHRONICLE_SEPARATOR = \
"""

--


"""
# -------------------------------------------------------------------

class EuchronismData(db.Model):
   """Store user messages."""
   user = db.UserProperty()
   chronicles = db.TextProperty()

def chronicle_key():
   return db.Key.from_path('Chronicle', '1')

def mail_admin(user_mail, message=None):
   """Send a mail to admin. If no message is specified,
   send an error traceback."""

   if message is None:
      message = ''.join(traceback.format_exception(
         sys.exc_type,
         sys.exc_value,
         sys.exc_traceback
      ))

   mail.send_mail(
       ADMAIL,
       ADMAIL,
       "Euchronism report",
       "%s:\n%s" % (user_mail, message)
   )
