# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-26 08:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Authv1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lv1', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Authv2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lv2', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Authv3',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lv3', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('lv1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publish.Authv1')),
                ('lv2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publish.Authv2')),
                ('lv3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publish.Authv3')),
            ],
        ),
    ]