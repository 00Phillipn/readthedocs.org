from django.conf import settings
from django.http import HttpResponsePermanentRedirect, SuspiciousOperation
from django.utils.http import urlquote

import re
from django import http

host_validation_re = re.compile(r"^([a-z0-9.-_]+|\[[a-f0-9]*:[a-f0-9:]+\])(:\d+)?$")
http.host_validation_re = host_validation_re

class UnderscoreMiddleware(object):
    def process_request(self, request):
        try:
            host = request.get_host()
        except SuspiciousOperation, ex:
            # Handle redirect of domains with _ in them.
            # HACK
            host = ex.message.replace('Invalid HTTP_HOST header: ', '')
            if '_' in host:
                host = host.replace('_', '-')
                new_uri = '%s://%s%s%s' % (
                    request.is_secure() and 'https' or 'http',
                    host,
                    urlquote(request.path),
                    (request.method == 'GET' and len(request.GET) > 0) and '?%s' % request.GET.urlencode() or ''
                )
                return HttpResponsePermanentRedirect(new_uri)
