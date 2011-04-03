from django.conf.urls.defaults import url, patterns, include

urlpatterns = patterns('',
    url(r'^(?P<lang_slug>\w{2})/(?P<version_slug>[\w.-]+)/(?P<filename>.+)$',
        'core.views.serve_docs',
        name='docs_detail'
    ),
    url(r'^(?P<lang_slug>\w{2})/(?P<version_slug>.*)/$',
        'core.views.serve_docs',
        {'filename': 'index.html'},
        name='docs_detail'
    ),
    url(r'^(?P<version_slug>.*)/$',
        'projects.views.public.subdomain_handler',
        name='version_subdomain_handler'
    ),
    url(r'^search/', include('haystack.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^$', 'projects.views.public.subdomain_handler')
)

