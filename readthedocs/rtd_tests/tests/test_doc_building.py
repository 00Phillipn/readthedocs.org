import base64
import json
import os
from os.path import join as pjoin
import shutil
from subprocess import check_call
from tempfile import mkdtemp

from django.conf import settings
from django.contrib.admin.models import User

from projects.models import Project
from projects import tasks

from .base import RTDTestCase

class TestBuilding(RTDTestCase):
    fixtures = ['eric.json']

    def make_test_git(self):
        directory = mkdtemp()
        cmd = ['git', 'init']
        check_call(cmd + [directory])
        path = os.getcwd()
        sample = os.path.abspath(pjoin(path, '../fixtures/sample_git'))
        shutil.copytree(sample, directory)
        check_call(['git', 'add', directory])
        check_call(['git', 'ci', '-m"init"'])
        return directory

    def setUp(self):
        repo = self.make_test_git()
        super(TestBuilding, self).setUp()
        self.eric = User.objects.get(username='eric')
        self.project = Project.objects.create(
            user = self.eric,
            name="Test Project",
            repo_type="git",
            #Our top-level checkout
            repo=repo
        )

    def test_default_project_build(self):
        """
        Test that a superuser can use the API
        """
        tasks.update_docs(pk=self.project.pk)
        self.assertTrue(os.path.exists(
            os.path.join(self.project.rtd_build_path(), 'index.html')
        ))

    '''
    def test_version_project_build(self):
        """
        Test that a superuser can use the API
        """
        tasks.update_docs(pk=self.project.pk, version_pk=self.version.pk)
        self.assertTrue(os.path.exists(
            os.path.join(self.project.rtd_build_path(), 'index.html')
        ))
    '''
