# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-10-31 10:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_usagelicense_extra'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usagelicense',
            name='num_seats',
            field=models.IntegerField(verbose_name='number of seats'),
        ),
    ]