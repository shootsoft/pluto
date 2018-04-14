#!/usr/bin/env python
import json
import urllib2

import jinja2
import os
import webapp2
from google.appengine.api import memcache

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


# [END imports]

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.tpl')
        self.response.write(template.render(self.query()))

    def query(self):
        client = memcache.Client()
        info = client.gets("release-info")
        if not info:
            contents = urllib2.urlopen(
                "https://api.github.com/repos/shootsoft/PlutoVideoSnapshoter/releases/latest").read()
            info = self.parse(contents)
            client.set("release-info", info, 3600 * 24 * 30)
        return info

    def parse(self, contents):
        contents = json.loads(contents)
        val = {'version': contents['tag_name'],
               'date': contents['published_at'][:10],
               'windows': {
                   'size': '',
                   'url': ''
               }, 'macOS': {
                'size': '',
                'url': ''
            }, 'linux': {
                'size': 'source',
                'url': contents['tarball_url']
            }}

        for item in contents['assets']:
            if 'macOS' in item['name']:
                val['macOS']['size'] = self.get_megabyte(item['size'])
                val['macOS']['url'] = item['browser_download_url']
            elif 'Windows' in item['name']:
                val['windows']['size'] = self.get_megabyte(item['size'])
                val['windows']['url'] = item['browser_download_url']

        return val

    def get_megabyte(self, bytes):
        return str(int(round(float(bytes) / 1024 / 1024))) + " MB"


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
