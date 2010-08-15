from celery.decorators import task
from celery.task.schedules import crontab
from celery.decorators import periodic_task

from projects.constants import SCRAPE_CONF_SETTINGS
from projects.models import Project
from projects.utils import  find_file, run

from builds.models import Build

import decimal
import os
import re
import glob
import fnmatch


ghetto_hack = re.compile(r'(?P<key>.*)\s*=\s*u?[\'\"](?P<value>.*)[\'\"]')

@task
def update_docs(pk):
    """
    A Celery task that updates the documentation for a project.
    """
    project = Project.objects.get(pk=pk)


    path = project.user_doc_path
    if not os.path.exists(path):
        os.makedirs(path)

    if project.is_imported:
        update_imported_docs(project)
        scrape_conf_file(project)
    else:
        update_created_docs(project)

    # kick off a build
    (ret, out, err) = build_docs(project)
    if not 'no targets are out of date.' in out:
        Build.objects.create(project=project, success=ret==0, output=out, error=err)
        if ret == 0:
            print "Build OK"
        else:
            print "Build ERROR"
    else:
        print "Build Unchanged"


def update_imported_docs(project):
    path = project.user_doc_path
    os.chdir(path)
    if os.path.exists(os.path.join(path, project.slug)):
        os.chdir(project.slug)
        if project.repo_type is 'hg':
            run('hg update -C -r . ')

        else:
            run('git fetch --git-dir=.git')
            run('git reset --hard origin/master --git-dir=.git')
    else:
        repo = project.repo
        if project.repo_type is 'hg':
            command = 'hg clone %s %s' % (repo, project.slug)
        else:
            repo = repo.replace('.git', '')
            command = 'git clone %s.git %s' % (repo, project.slug)
        run(command)


def scrape_conf_file(project):
    conf_dir = project.find('conf.py')[0].replace('/conf.py', '')
    os.chdir(conf_dir)
    lines = open('conf.py').readlines()
    data = {}
    for line in lines:
        for we_care in SCRAPE_CONF_SETTINGS:
            match = ghetto_hack.search(line)
            if match:
                data[match.group(1).strip()] = match.group(2).strip()
    project.copyright = data['copyright']
    project.theme = data.get('html_theme', 'default')
    project.suffix = data.get('source_suffix', '.rst')
    project.path = os.getcwd()

    try:
        project.version = decimal.Decimal(data.get('version', '0.1.0'))
    except decimal.InvalidOperation:
        project.version = ''

    project.save()


def update_created_docs(project):
    # grab the root path for the generated docs to live at
    path = project.user_doc_path

    doc_root = os.path.join(path, project.slug, 'docs')

    if not os.path.exists(doc_root):
        os.makedirs(doc_root)

    project.path = doc_root
    project.save()

    project.write_index()

    for file in project.files.all():
        file.write_to_disk()


def build_docs(project):
    """
    A helper function for the celery task to do the actual doc building.
    """
    project.write_to_disk()

    try:
        makes = [makefile for makefile in project.find('Makefile') if 'doc' in makefile]
        make_dir = makes[0].replace('/Makefile', '')
        os.chdir(make_dir)
        (ret, out, err) = run('make html')
    except IndexError:
        os.chdir(project.path)
        (ret, out, err) = run('sphinx-build -b html . _build/html')
    return (ret, out, err)


#@periodic_task(run_every=crontab(hour="*", minute="*/30", day_of_week="*"))
@periodic_task(run_every=crontab(hour="*", minute="*", day_of_week="*"))
def update_docs_pull():
    for project in Project.objects.all():
        print "Building %s" % project
        update_docs(pk=project.pk)
