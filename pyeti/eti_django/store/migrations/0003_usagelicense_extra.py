# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-10-30 12:04
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_auto_20180807_1214'),
    ]

    operations = [
        migrations.AddField(
            model_name='usagelicense',
            name='extra',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
    ]