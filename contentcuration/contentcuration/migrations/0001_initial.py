# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-12 17:33
from __future__ import unicode_literals

import contentcuration.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import mptt.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
        ),
        migrations.CreateModel(
            name='AssessmentItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default=b'multiplechoice', max_length=50)),
                ('question', models.TextField(blank=True)),
                ('answers', models.TextField(default=b'[]')),
            ],
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', contentcuration.models.UUIDField(default=uuid.uuid4, max_length=32, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(blank=True, max_length=400)),
                ('version', models.IntegerField(default=0)),
                ('thumbnail', models.TextField(blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('public', models.BooleanField(default=False)),
                ('bookmarked_by', models.ManyToManyField(related_name='bookmarked_channels', to=settings.AUTH_USER_MODEL, verbose_name='bookmarked by')),
            ],
            options={
                'verbose_name': 'Channel',
                'verbose_name_plural': 'Channels',
            },
        ),
        migrations.CreateModel(
            name='ContentKind',
            fields=[
                ('kind', models.CharField(choices=[(b'topic', 'Topic'), (b'video', 'Video'), (b'audio', 'Audio'), (b'exercise', 'Exercise'), (b'document', 'Document'), (b'image', 'Image')], max_length=200, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='ContentNode',
            fields=[
                ('id', contentcuration.models.UUIDField(default=uuid.uuid4, max_length=32, primary_key=True, serialize=False)),
                ('content_id', contentcuration.models.UUIDField(default=uuid.uuid4, editable=False, max_length=32)),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(blank=True, max_length=400)),
                ('sort_order', models.FloatField(default=0, help_text='Ascending, lowest number shown first', max_length=50, verbose_name='sort order')),
                ('license_owner', models.CharField(blank=True, help_text='Organization of person who holds the essential rights', max_length=200)),
                ('author', models.CharField(blank=True, help_text='Person who created content', max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modified')),
                ('changed', models.BooleanField(default=True)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('cloned_source', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clones', to='contentcuration.ContentNode')),
            ],
            options={
                'verbose_name': 'Topic',
                'verbose_name_plural': 'Topics',
            },
            managers=[
                ('_default_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ContentTag',
            fields=[
                ('id', contentcuration.models.UUIDField(default=uuid.uuid4, max_length=32, primary_key=True, serialize=False)),
                ('tag_name', models.CharField(max_length=30)),
                ('channel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='contentcuration.Channel')),
            ],
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Title', help_text='Title of the content item', max_length=50, verbose_name='title')),
                ('description', models.TextField(default='Description', help_text='Brief description of what this content item is', max_length=200, verbose_name='description')),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', contentcuration.models.UUIDField(default=uuid.uuid4, max_length=32, primary_key=True, serialize=False)),
                ('checksum', models.CharField(blank=True, max_length=400)),
                ('file_size', models.IntegerField(blank=True, null=True)),
                ('file_on_disk', models.FileField(blank=True, max_length=500, storage=contentcuration.models.FileOnDiskStorage(), upload_to=contentcuration.models.file_on_disk_name)),
                ('original_filename', models.CharField(blank=True, max_length=255)),
                ('contentnode', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='contentcuration.ContentNode')),
            ],
        ),
        migrations.CreateModel(
            name='FileFormat',
            fields=[
                ('extension', models.CharField(choices=[(b'mp4', 'mp4'), (b'vtt', 'vtt'), (b'srt', 'srt'), (b'mp3', 'mp3'), (b'pdf', 'pdf')], max_length=40, primary_key=True, serialize=False)),
                ('mimetype', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='FormatPreset',
            fields=[
                ('id', models.CharField(choices=[(b'high_res_video', 'High resolution video'), (b'low_res_video', 'Low resolution video'), (b'vector_video', 'Vertor video'), (b'thumbnail', 'Thumbnail'), (b'thumbnail', 'Thumbnail'), (b'caption', 'Caption')], max_length=150, primary_key=True, serialize=False)),
                ('readable_name', models.CharField(max_length=400)),
                ('multi_language', models.BooleanField(default=False)),
                ('supplementary', models.BooleanField(default=False)),
                ('order', models.IntegerField()),
                ('allowed_formats', models.ManyToManyField(blank=True, to='contentcuration.FileFormat')),
                ('kind', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='format_presets', to='contentcuration.ContentKind')),
            ],
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', contentcuration.models.UUIDField(default=uuid.uuid4, max_length=32, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=100)),
                ('first_name', models.CharField(default=b'Guest', max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('channel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pending_editors', to='contentcuration.Channel')),
                ('invited', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_to', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Invitation',
                'verbose_name_plural': 'Invitations',
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang_code', models.CharField(db_index=True, max_length=2)),
                ('lang_subcode', models.CharField(db_index=True, max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('license_name', models.CharField(max_length=50)),
                ('license_url', models.URLField(blank=True)),
                ('license_description', models.TextField(blank=True)),
                ('exists', models.BooleanField(default=False, help_text='Tells whether or not a content item is licensed to share', verbose_name='license exists')),
            ],
        ),
        migrations.CreateModel(
            name='PrerequisiteContentRelationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prerequisite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contentcuration_prerequisitecontentrelationship_prerequisite', to='contentcuration.ContentNode')),
                ('target_node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contentcuration_prerequisitecontentrelationship_target_node', to='contentcuration.ContentNode')),
            ],
        ),
        migrations.CreateModel(
            name='RelatedContentRelationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contentnode_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contentcuration_relatedcontentrelationship_1', to='contentcuration.ContentNode')),
                ('contentnode_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contentcuration_relatedcontentrelationship_2', to='contentcuration.ContentNode')),
            ],
        ),
        migrations.AddField(
            model_name='file',
            name='file_format',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='contentcuration.FileFormat'),
        ),
        migrations.AddField(
            model_name='file',
            name='lang',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contentcuration.Language'),
        ),
        migrations.AddField(
            model_name='file',
            name='preset',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='contentcuration.FormatPreset'),
        ),
        migrations.AddField(
            model_name='contentnode',
            name='is_related',
            field=models.ManyToManyField(blank=True, related_name='relate_to', through='contentcuration.RelatedContentRelationship', to='contentcuration.ContentNode'),
        ),
        migrations.AddField(
            model_name='contentnode',
            name='kind',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contentnodes', to='contentcuration.ContentKind'),
        ),
        migrations.AddField(
            model_name='contentnode',
            name='license',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contentcuration.License'),
        ),
        migrations.AddField(
            model_name='contentnode',
            name='original_node',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='duplicates', to='contentcuration.ContentNode'),
        ),
        migrations.AddField(
            model_name='contentnode',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='contentcuration.ContentNode'),
        ),
        migrations.AddField(
            model_name='contentnode',
            name='prerequisite',
            field=models.ManyToManyField(blank=True, related_name='is_prerequisite_of', through='contentcuration.PrerequisiteContentRelationship', to='contentcuration.ContentNode'),
        ),
        migrations.AddField(
            model_name='contentnode',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='tagged_content', to='contentcuration.ContentTag'),
        ),
        migrations.AddField(
            model_name='channel',
            name='clipboard_tree',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='channel_clipboard', to='contentcuration.ContentNode'),
        ),
        migrations.AddField(
            model_name='channel',
            name='editors',
            field=models.ManyToManyField(help_text='Users with edit rights', related_name='editable_channels', to=settings.AUTH_USER_MODEL, verbose_name='editors'),
        ),
        migrations.AddField(
            model_name='channel',
            name='main_tree',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='channel_main', to='contentcuration.ContentNode'),
        ),
        migrations.AddField(
            model_name='channel',
            name='trash_tree',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='channel_trash', to='contentcuration.ContentNode'),
        ),
        migrations.AddField(
            model_name='assessmentitem',
            name='exercise',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_assessment_items', to='contentcuration.Exercise'),
        ),
        migrations.AlterUniqueTogether(
            name='relatedcontentrelationship',
            unique_together=set([('contentnode_1', 'contentnode_2')]),
        ),
        migrations.AlterUniqueTogether(
            name='prerequisitecontentrelationship',
            unique_together=set([('target_node', 'prerequisite')]),
        ),
        migrations.AlterUniqueTogether(
            name='contenttag',
            unique_together=set([('tag_name', 'channel')]),
        ),
    ]
