# -*- coding: UTF-8 -*-
# notification is part of Band Cochon
# Band Cochon (c) Prince Cuberdon 2011 and Later <princecuberdon@bandcochon.fr>

from django.contrib import admin

from .models import Template


class BaseAdmin(admin.ModelAdmin):
    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js',
        )


class TemplateAdmin(BaseAdmin):
    list_display = ('resume', 'shortcut',)


class PreferenceAdmin(BaseAdmin):
    list_display = ('name', 'default2string', 'sendmail', 'anonymous', 'username', 'offuscate_pass', 'server',)


admin.site.register(Template, TemplateAdmin)
