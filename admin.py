# -*- coding: UTF-8 -*-
# notification is part of Band Cochon
# Band Cochon (c) Prince Cuberdon 2011 and Later <princecuberdon@bandcochon.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# notification is part of Band Cochon
# Band Cochon (c) Prince Cuberdon 2011 and Later <princecuberdon@bandcochon.fr>

from django.contrib import admin

from .models import Preference, Template, MailingList


class BaseAdmin(admin.ModelAdmin):
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js',
        )


class TemplateAdmin(BaseAdmin):
    list_display = ('resume', 'shortcut',)


class PreferenceAdmin(BaseAdmin):
    list_display = ('name', 'default2string', 'sendmail', 'anonymous', 'username', 'offuscate_pass', 'server',)


admin.site.register(Preference, PreferenceAdmin)
admin.site.register(Template, TemplateAdmin)
admin.site.register(MailingList, BaseAdmin)
