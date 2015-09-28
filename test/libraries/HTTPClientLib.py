import json
import requests
__author__ = 'shawkins'
"""
Yes, this filename does not comply with PEP8. Thank robotframework for that.
"""

class HTTPClientLib(object):
    def get_http_status_from_request(self, request):
        return request.status_code

    def get_http_content_from_request(self, request):
        return request.content

    def get_http_json_content_from_request(self, request):
        return json.loads(request.content)

    def get_url(self, url):
        return requests.get(url)

    def post_to_url(self, url, data):
        return requests.post(url, data)

    def delete_url(self, url, data=None):
        return requests.delete(url, data=data)
