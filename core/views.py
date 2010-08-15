from django.conf import settings
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_view_exempt
from django.views.static import serve

import json
import os

from projects.models import Project
from projects.tasks import update_docs
from projects.utils import find_file
from watching.models import PageView


def homepage(request):
    projs = Project.objects.all()[:5]
    updated = PageView.objects.all()[:5]
    return render_to_response('homepage.html',
                              {'project_list': projs,
                               'updated_list': updated},
                context_instance=RequestContext(request))

@csrf_view_exempt
def github_build(request):
    obj = json.loads(request.POST['payload'])
    name = obj['repository']['name']
    url = obj['repository']['url']
    project = Project.objects.get(repo=url)
    update_docs.delay(pk=project.pk)
    return HttpResponse('Build Started')

def serve_docs(request, username, project_slug, filename):
    proj = Project.objects.get(slug=project_slug, user__username=username)
    if not filename:
        filename = "index.html"
    filename = filename.rstrip('/')
    if not os.path.exists(os.path.join(proj.full_html_path, filename)):
            return HttpResponse("These docs haven't been built yet :(")
    if 'html' in filename:
        pageview, created = PageView.objects.get_or_create(project=proj, url=filename)
        if not created:
            pageview.count = F('count') + 1
            pageview.save()
    return serve(request, filename, proj.full_html_path)

def render_header(request):
    return render_to_response('core/header.html', {},
                context_instance=RequestContext(request))
