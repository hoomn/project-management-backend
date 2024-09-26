# Generated by Django 5.1.1 on 2024-09-26 03:24

import django.db.models.deletion
import pm.utils
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time when the record was created.', verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The date and time when the record was last modified.', verbose_name='Updated at')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=128, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created_by', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(blank=True, related_name='%(class)s_membership', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time when the record was created.', verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The date and time when the record was last modified.', verbose_name='Updated at')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=128, verbose_name='Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Start Date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End Date')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Done'), (2, 'Ready'), (3, 'On Track'), (4, 'Off Track'), (5, 'On Hold'), (6, 'Not Started')], default=6, verbose_name='Status')),
                ('priority', models.PositiveSmallIntegerField(choices=[(6, 'Critical'), (5, 'High'), (4, 'Upper Medium'), (3, 'Medium'), (2, 'Lower Medium'), (1, 'Low')], default=3, verbose_name='Priority')),
                ('is_archived', models.BooleanField(default=False, verbose_name='Has been archived')),
                ('assigned_to', models.ManyToManyField(blank=True, related_name='%(class)s_assigned_to', to=settings.AUTH_USER_MODEL, verbose_name='Assigned to')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='pm.domain', verbose_name='Parent Domain')),
            ],
            options={
                'ordering': ['-status', models.OrderBy(models.F('end_date'), nulls_last=True), '-priority'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time when the record was created.', verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The date and time when the record was last modified.', verbose_name='Updated at')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=128, verbose_name='Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Start Date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End Date')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Done'), (2, 'Ready'), (3, 'On Track'), (4, 'Off Track'), (5, 'On Hold'), (6, 'Not Started')], default=6, verbose_name='Status')),
                ('priority', models.PositiveSmallIntegerField(choices=[(6, 'Critical'), (5, 'High'), (4, 'Upper Medium'), (3, 'Medium'), (2, 'Lower Medium'), (1, 'Low')], default=3, verbose_name='Priority')),
                ('is_archived', models.BooleanField(default=False, verbose_name='Has been archived')),
                ('assigned_to', models.ManyToManyField(blank=True, related_name='%(class)s_assigned_to', to=settings.AUTH_USER_MODEL, verbose_name='Assigned to')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='pm.project', verbose_name='Parent Project')),
            ],
            options={
                'ordering': ['-status', models.OrderBy(models.F('end_date'), nulls_last=True), '-priority'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Subtask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time when the record was created.', verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The date and time when the record was last modified.', verbose_name='Updated at')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=128, verbose_name='Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Start Date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End Date')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Done'), (2, 'Ready'), (3, 'On Track'), (4, 'Off Track'), (5, 'On Hold'), (6, 'Not Started')], default=6, verbose_name='Status')),
                ('priority', models.PositiveSmallIntegerField(choices=[(6, 'Critical'), (5, 'High'), (4, 'Upper Medium'), (3, 'Medium'), (2, 'Lower Medium'), (1, 'Low')], default=3, verbose_name='Priority')),
                ('is_archived', models.BooleanField(default=False, verbose_name='Has been archived')),
                ('assigned_to', models.ManyToManyField(blank=True, related_name='%(class)s_assigned_to', to=settings.AUTH_USER_MODEL, verbose_name='Assigned to')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='pm.task', verbose_name='Parent Task')),
            ],
            options={
                'ordering': ['-status', models.OrderBy(models.F('end_date'), nulls_last=True), '-priority'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('C', 'Create'), ('U', 'Update'), ('D', 'Delete')], default='C', max_length=1)),
                ('content', models.JSONField(default=dict, verbose_name='Content')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'activity',
                'verbose_name_plural': 'activities',
                'ordering': ['-created_at'],
                'abstract': False,
                'indexes': [models.Index(fields=['content_type', 'object_id'], name='pm_activity_content_0e7340_idx')],
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time when the record was created.', verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The date and time when the record was last modified.', verbose_name='Updated at')),
                ('object_id', models.PositiveIntegerField()),
                ('is_updated', models.BooleanField(default=False)),
                ('file', models.FileField(upload_to=pm.utils.attachment_upload_path)),
                ('file_name', models.CharField(blank=True, max_length=255, null=True)),
                ('file_size', models.BigIntegerField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('content_type', models.ForeignKey(limit_choices_to={'app_label': 'pm', 'model__in': ('project', 'task', 'subtask')}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
            ],
            options={
                'ordering': ['created_at'],
                'abstract': False,
                'indexes': [models.Index(fields=['content_type', 'object_id'], name='pm_attachme_content_8a73fa_idx')],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time when the record was created.', verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The date and time when the record was last modified.', verbose_name='Updated at')),
                ('object_id', models.PositiveIntegerField()),
                ('is_updated', models.BooleanField(default=False)),
                ('text', models.TextField()),
                ('content_type', models.ForeignKey(limit_choices_to={'app_label': 'pm', 'model__in': ('project', 'task', 'subtask')}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
            ],
            options={
                'ordering': ['created_at'],
                'abstract': False,
                'indexes': [models.Index(fields=['content_type', 'object_id'], name='pm_comment_content_d769b8_idx')],
            },
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.UniqueConstraint(fields=('domain', 'title'), name='unique_domain_title'),
        ),
        migrations.AddConstraint(
            model_name='task',
            constraint=models.UniqueConstraint(fields=('project', 'title'), name='unique_project_title'),
        ),
        migrations.AddConstraint(
            model_name='subtask',
            constraint=models.UniqueConstraint(fields=('task', 'title'), name='unique_task_title'),
        ),
    ]