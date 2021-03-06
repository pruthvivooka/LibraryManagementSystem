# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-16 10:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Borrower',
            fields=[
                ('borrower_id', models.AutoField(db_column='borrower_id', primary_key=True, serialize=False)),
                ('ssn', models.CharField(db_column='ssn', max_length=9, unique=True)),
                ('first_name', models.CharField(db_column='first_name', max_length=30)),
                ('last_name', models.CharField(db_column='last_name', max_length=30)),
                ('email', models.EmailField(db_column='email', max_length=254, unique=True)),
                ('address', models.CharField(db_column='address', max_length=250)),
                ('city', models.CharField(db_column='city', max_length=30)),
                ('state', models.CharField(db_column='state', max_length=2)),
                ('phone', models.CharField(db_column='phone', max_length=10)),
            ],
            options={
                'db_table': 'borrowers',
            },
        ),
    ]
