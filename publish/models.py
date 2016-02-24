from __future__ import unicode_literals

from django.db import models



# Create your models here.

class Authv1(models.Model):
    lv1 = models.CharField(max_length=50)
    def __unicode__(self):
        return self.lv1

class Authv2(models.Model):
    lv2 = models.CharField(max_length=50)
    def __unicode__(self):
        return self.lv2

class Authv3(models.Model):
    lv3 = models.CharField(max_length=50)
    def __unicode__(self):
        return self.lv3


class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    lv1 = models.ForeignKey(Authv1)
    lv2 = models.ForeignKey(Authv2)
    lv3 = models.ForeignKey(Authv3)
    def __unicode__(self):
        return self.username
