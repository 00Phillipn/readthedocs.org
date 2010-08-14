from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list, object_detail

from project.models import Project


def project_index(request, username=None):
    queryset = Project.objects.all()
    if username:
        user = get_object_or_404(User, username=username)
        queryset = queryset.filter(user=user)
    else:
        user = None

    return object_list(
        request,
        queryset=queryset,
        extra_context={'user': user},
        paginate_by=20,
        page=int(request.GET.get('page', 1)),
        template_object_name='project',
    )

def project_detail(request, username, project_slug):
    user = get_object_or_404(User, username=username)
    queryset = user.projects.all()
    
    return object_detail(
        request,
        queryset=queryset,
        slug_field='slug',
        slug=project_slug,
        extra_context={'user': user},
        template_object_name='project',
    )
