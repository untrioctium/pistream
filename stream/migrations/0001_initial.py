# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('ascii_name', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['artist__name', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('ascii_name', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MusicTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, max_length=100, verbose_name='Slug')),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.CreateModel(
            name='TaggedMusic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.IntegerField(verbose_name='Object id', db_index=True)),
                ('content_type', models.ForeignKey(related_name='stream_taggedmusic_tagged_items', verbose_name='Content type', to='contenttypes.ContentType')),
                ('tag', models.ForeignKey(related_name='stream_taggedmusic_items', to='stream.MusicTag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trackno', models.IntegerField()),
                ('title', models.CharField(max_length=200)),
                ('relpath', models.CharField(max_length=1000)),
                ('length', models.IntegerField()),
                ('playcount', models.IntegerField(default=0)),
                ('ascii_title', models.CharField(max_length=200)),
                ('album', models.ForeignKey(to='stream.Album')),
                ('artist', models.ForeignKey(to='stream.Artist')),
                ('tags', taggit.managers.TaggableManager(to='stream.MusicTag', through='stream.TaggedMusic', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'ordering': ['album__name', 'relpath'],
            },
        ),
        migrations.AddField(
            model_name='artist',
            name='tags',
            field=taggit.managers.TaggableManager(to='stream.MusicTag', through='stream.TaggedMusic', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='album',
            name='artist',
            field=models.ForeignKey(to='stream.Artist'),
        ),
        migrations.AddField(
            model_name='album',
            name='tags',
            field=taggit.managers.TaggableManager(to='stream.MusicTag', through='stream.TaggedMusic', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
    ]
