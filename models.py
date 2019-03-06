# -*- coding: UTF-8 -*-
# notification is part of Band Cochon
# Band Cochon (c) Prince Cuberdon 2011 and Later <princecuberdon@bandcochon.fr>

from django.db import models

from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


class Template(models.Model):
    resume = models.CharField(max_length=255, help_text=u"Résumé du mail", verbose_name=u"Résumé")
    shortcut = models.CharField(max_length=20, help_text=u"Raccourci utilisé en interne", verbose_name="Raccourci")
    subject = models.CharField(max_length=255, help_text="Sujet", verbose_name="Sujet")
    body = models.TextField(help_text="Corps du message", verbose_name="Corps")

    def __unicode__(self):
        return self.resume

    class Meta:
        app_label = "notification"
