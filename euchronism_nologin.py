# -*- coding: utf-8 -*-

import os

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template


class FAQ(webapp.RequestHandler):

   def get(self):
      dot = os.path.dirname(__file__)
      template_path = os.path.join(dot, 'euchronism_template.html')
      content_path = os.path.join(dot, 'content', 'FAQ_content.html')

      template_values = {
         'page_title': 'Euchronism FAQ',
         'page_content': open(content_path).read(),
      }
      self.response.out.write(
         template.render(template_path, template_values)
      )


application = webapp.WSGIApplication([
   ('/FAQ.html?', FAQ),
], debug=True)


def main():
   run_wsgi_app(application)


if __name__ == '__main__':
   main()
