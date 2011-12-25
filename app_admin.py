# -*- coding: utf-8 -*-
"""
"""

import sys
import traceback

from google.appengine.api import mail
from google.appengine.ext import db

# -------------------------------------------------------------------
ADMAIL = 'euchronism.mailer@gmail.com'
MIN_TIME_DELTA = 14 # send min 2 weeks from now
CHRONICLE_SEPARATOR = \
"""

--

"""
# -------------------------------------------------------------------

class EuchronismData(db.Model):
   """Store user messages."""
   user = db.UserProperty()
   lightrays = db.TextProperty()

def lightray_key():
   return db.Key.from_path('Lightray', '1')

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
