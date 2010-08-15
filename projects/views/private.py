import simplejson
import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.template.defaultfilters import linebreaks
from django.views.generic.list_detail import object_list

from projects.forms import FileForm, CreateProjectForm, ImportProjectForm, ConfForm, FileRevisionForm
from projects.models import Project, File


@login_required
def project_dashboard(request):
    return object_list(
        request,
        queryset=request.user.projects.all(),
        page=int(request.GET.get('page', 1)),
        template_object_name='project',
        template_name='projects/project_dashboard.html',
    )

@login_required
def project_manage(request, project_slug):
    project = get_object_or_404(request.user.projects.all(), slug=project_slug)
    return object_list(
        request,
        queryset=project.files.all(),
        extra_context={'project': project},
        page=int(request.GET.get('page', 1)),
        template_object_name='file',
        template_name='projects/project_manage.html',
    )

@login_required
def project_configure(request, project_slug):
    project = get_object_or_404(request.user.projects.all(), slug=project_slug)

    form = ConfForm(instance=project.conf, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        conf = form.save()
        manage = reverse('projects_manage', args=[project.slug])
        return HttpResponseRedirect(manage)

    return render_to_response(
        'projects/project_configure.html',
        {'project': project, 'conf': project.conf, 'form': form},
        context_instance=RequestContext(request)
    )

@login_required
def project_create(request):
    """
    A form for creating a brand new project?
    """
    form = CreateProjectForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.instance.user = request.user
        project = form.save()
        project_manage = reverse('projects_manage', args=[project.slug])
        return HttpResponseRedirect(project_manage)

    return render_to_response(
        'projects/project_create.html',
        {'form': form},
        context_instance=RequestContext(request)
    )

@login_required
def project_edit(request, project_slug):
    project = get_object_or_404(request.user.projects.all(), slug=project_slug)

    if project.is_imported:
        form_class = ImportProjectForm
    else:
        form_class = CreateProjectForm

    form = form_class(instance=project, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        project_dashboard = reverse('projects_dashboard')
        return HttpResponseRedirect(project_dashboard)

    return render_to_response(
        'projects/project_edit.html',
        {'form': form, 'project': project},
        context_instance=RequestContext(request)
    )

@login_required
def project_delete(request, project_slug):
    project = get_object_or_404(request.user.projects.all(), slug=project_slug)

    if request.method == 'POST':
        project.delete()
        project_dashboard = reverse('projects_dashboard')
        return HttpResponseRedirect(project_dashboard)

    return render_to_response(
        'projects/project_delete.html',
        {'project': project},
        context_instance=RequestContext(request)
    )

@login_required
def project_import(request):
    """
    I guess a form here for configuring your import?
    """
    form = ImportProjectForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.instance.user = request.user
        project = form.save()
        project_manage = reverse('projects_manage', args=[project.slug])
        return HttpResponseRedirect(project_manage)

    return render_to_response(
        'projects/project_import.html',
        {'form': form},
        context_instance=RequestContext(request)
    )

@login_required
def file_add(request, project_slug):
    project = get_object_or_404(request.user.projects.all(), slug=project_slug)
    file = File(project=project)

    form = FileForm(instance=file, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.instance.project = project
        file = form.save()
        project_manage = reverse('projects_manage', args=[project.slug])
        return HttpResponseRedirect(project_manage)

    return render_to_response(
        'projects/file_add.html',
        {'form': form, 'project': project},
        context_instance=RequestContext(request)
    )

@login_required
def file_edit(request, project_slug, file_id):
    project = get_object_or_404(request.user.projects.all(), slug=project_slug)
    file = get_object_or_404(project.files.all(), pk=file_id)

    form = FileForm(instance=file, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        project_manage = reverse('projects_manage', args=[project.slug])
        return HttpResponseRedirect(project_manage)

    return render_to_response(
        'projects/file_edit.html',
        {'form': form, 'project': project},
        context_instance=RequestContext(request)
    )

@login_required
def file_delete(request, project_slug, file_id):
    project = get_object_or_404(request.user.projects.all(), slug=project_slug)
    file = get_object_or_404(project.files.all(), pk=file_id)

    if request.method == 'POST':
        file.delete()
        project_manage = reverse('projects_manage', args=[project.slug])
        return HttpResponseRedirect(project_manage)

    return render_to_response(
        'projects/file_delete.html',
        {'project': project},
        context_instance=RequestContext(request)
    )

@login_required
def file_history(request, project_slug, file_id):
    project = get_object_or_404(request.user.projects.all(), slug=project_slug)
    file = get_object_or_404(project.files.all(), pk=file_id)

    form = FileRevisionForm(file, request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.cleaned_data['revision'].apply()
        history = reverse('projects_file_history', args=[project.slug, file.pk])
        return HttpResponseRedirect(history)

    return object_list(
        request,
        queryset=file.revisions.all(),
        extra_context={'project': project, 'file': file, 'form': form},
        page=int(request.GET.get('page', 1)),
        template_object_name='revision',
        template_name='projects/file_history.html',
    )

@login_required
def file_diff(request, project_slug, file_id, from_id, to_id):
    project = get_object_or_404(request.user.projects.all(), slug=project_slug)
    file = get_object_or_404(project.files.all(), pk=file_id)

    # grab the requested revisions
    from_rev = get_object_or_404(file.revisions.all(), pk=from_id)
    to_rev = get_object_or_404(file.revisions.all(), pk=to_id)

    # generate a pretty html diff
    diff = file.get_html_diff(from_rev.revision_number, to_rev.revision_number)
    contents = linebreaks(to_rev.get_file_content())

    payload = {
        'diff': diff,
        'contents': contents
    }

    # return it assuming json
    return HttpResponse(simplejson.dumps(payload), mimetype='text/javascript')

@login_required
def export(request, project_slug):
    project = Project.objects.get(user=request.user, slug=project_slug)
    os.chdir(project.user_doc_path)
    dir_path = os.path.join(settings.MEDIA_ROOT, 'export', project.user.username)
    file_path = os.path.join(dir_path, '%s.zip' % project.slug)
    try:
        os.makedirs(dir_path)
    except OSError:
        #Directory already exists
        pass
    os.system('zip -r %s *' % file_path)
    return HttpResponseRedirect(os.path.join(settings.MEDIA_URL, 'export', project.user.username, '%s.zip' % project.slug))
