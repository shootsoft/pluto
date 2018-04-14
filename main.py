#!/usr/bin/env python
import json
import logging

import cloudstorage
import jinja2
import os
import webapp2
from google.appengine.api import memcache, urlfetch, app_identity

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# [START retries]
cloudstorage.set_default_retry_params(
    cloudstorage.RetryParams(
        initial_delay=0.2, max_delay=5.0, backoff_factor=2, max_retry_period=15
    ))


# [END retries]

# [END imports]

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.tpl')
        self.response.write(template.render(self.query()))

    def query(self):
        client = memcache.Client()
        info = client.gets("release-info")
        if not info:
            result = urlfetch.fetch(self.get_github_url())
            if result.status_code == 200:
                info = self.parse(result.content)
                client.set("release-info", info, 3600 * 24 * 30)
            else:
                logging.error(result.status_code)
        if not info:
            info = {}
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

    def get_github_url(self):
        bucket_name = os.environ.get(
            'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        with cloudstorage.open("/" + bucket_name + "/token/github.aip.token") as sfile:
            return "https://api.github.com/repos/shootsoft/PlutoVideoSnapshoter/releases/latest?access_token=" + sfile.readline()


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
