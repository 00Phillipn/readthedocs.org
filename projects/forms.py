import os

from django import forms
from django.template.loader import render_to_string

from projects import constants
from projects.models import Project, File, Conf
from projects.tasks import update_docs


class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ('user', 'slug', 'repo', 'docs_directory',)

    def save(self, *args, **kwargs):
        # save the project
        project = super(CreateProjectForm, self).save(*args, **kwargs)

        # create a couple sample files
        for i, (sample_file, template) in enumerate(constants.SAMPLE_FILES):
            File.objects.create(
                project=project,
                heading=sample_file,
                content=render_to_string(template, {'project': project}),
                ordering=i+1,
            )
        return project


class ImportProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ('user', 'slug', 'version',)

    def save(self, *args, **kwargs):
        # save the project
        project = super(ImportProjectForm, self).save(*args, **kwargs)

        # kick off the celery job
        update_docs.delay(pk=project.pk)
        return project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ('user', 'slug')


class FileForm(forms.ModelForm):
    revision_comment = forms.CharField(max_length=255, required=False)
    
    class Meta:
        model = File
        exclude = ('project', 'slug')
    
    def save(self, *args, **kwargs):
        # grab the old content before saving
        old_content = self.initial.get('content', '')
        
        # save the file object
        file_obj = super(FileForm, self).save(*args, **kwargs)
        
        # create a new revision from the old content -> new
        file_obj.create_revision(
            old_content,
            self.cleaned_data.get('revision_comment', '')
        )

        update_docs.delay(file_obj.project)


class ConfForm(forms.ModelForm):
    class Meta:
        model = Conf
        exclude = ('project',)
