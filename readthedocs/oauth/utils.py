import logging

from .models import GithubProject, GithubOrganization

log = logging.getLogger(__name__)

def make_github_project(user, org, privacy, repo_json):
    if (repo_json['private'] is True and privacy == 'private' or 
           repo_json['private'] is False and privacy == 'public'):
        project, created = GithubProject.objects.get_or_create(
            user=user,
            organization=org,
            full_name=repo_json['full_name'],
        )
        project.name = repo_json['name']
        project.description = repo_json['description']
        project.git_url = repo_json['git_url']
        project.ssh_url = repo_json['ssh_url']
        project.html_url = repo_json['html_url']
        project.json = repo_json
        project.save()
        return project
    else:
        log.debug('Not importing %s because mismatched type' % repo_json['name'])

def make_github_organization(user, org_json):
    org, created = GithubOrganization.objects.get_or_create(
        login=org_json.get('login'),
        html_url=org_json.get('html_url'),
        name=org_json.get('name'),
        email=org_json.get('email'),
        json=org_json,
    )
    org.users.add(user)
    return org
