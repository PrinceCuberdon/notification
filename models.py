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

from django.db import models

from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


class PreferenceManager(models.Manager):
    def get_default(self):
        """ Return the current preference """
        return Preference.objects.filter(default_account=True).latest('id')  # , active=True)


class Preference(models.Model):
    name = models.CharField(max_length=40, help_text=u"Nom du serveur", verbose_name=u"Nom")
    webmaster = models.EmailField(help_text=u"Adresse mail du webmaster", blank=True)
    sendmail = models.EmailField(help_text=u"Email par default pour l'envoi d\'email", verbose_name=u"Email")
    anonymous = models.BooleanField(default=False)
    username = models.CharField(blank=True, null=True, max_length=40, help_text=u"Nom d'utilisateur",
                                verbose_name=u"Utilisateur")
    password = models.CharField(blank=True, null=True, max_length=40, help_text=u"Mot de passe",
                                verbose_name="Mot de passe")
    server = models.CharField(max_length=255, help_text=u"Adresse du serveur", verbose_name="Serveur")
    port = models.IntegerField(default=25, help_text=u"Port du serveur")
    default_account = models.BooleanField(default=False, help_text=u"Serveur par défaut",
                                          verbose_name=u"Compte par défaut")

    objects = PreferenceManager()

    class Meta:
        app_label = "notification"

    def __unicode__(self):
        return self.name

    # Admin zone
    def offuscate_pass(self):
        return "*" * len(self.password)

    offuscate_pass.short_description = u"Mot de passe"

    def default2string(self):
        if self.default_account:
            return "Oui"
        return "Non"

    default2string.short_description = u"Compte par défaut"


class MailingList(models.Model):
    """ Todo: this model must be widly modified """
    creation = models.DateField(auto_now=True)
    subject = models.CharField(max_length=150, help_text="Sujet du message", verbose_name="Sujet")
    content = models.TextField(verbose_name="Message", help_text="Corps du message.")

    send_to_all = models.BooleanField(default=False,
                                      verbose_name=u"Envoyer à tous",
                                      help_text=u"Envoyer le message à tous les utilisateurs inscripts")

    send_to_inactive = models.BooleanField(default=False,
                                           verbose_name=u"Envoyer aux inactifs",
                                           help_text=u"Envoyer le message à tous les utilisateurs qui ne participent pas")

    class Meta:
        app_label = "notification"

    def __unicode__(self):
        return self.subject

    def save(self, *args, **kwargs):
        """ Due to cross import, can't directly import Utilisateur """
        # 
        if self.send_to_all or self.send_to_inactive:  # or self.send_to_active
            authusers = User.objects.filter(is_superuser=False).only('email')
            users = []
            if self.send_to_inactive:
                for u in authusers:
                    try:
                        if u.profile.get_picture_count() == 0:
                            users.append(u)
                    except ObjectDoesNotExist:
                        pass

            else:
                users = authusers

            from notification import Notification

            notif = Notification(debug=settings.IS_LOCAL)
            notif.set_content(self.subject, self.content)
            for u in users:
                notif.push(u.email)
            notif.send(debug=settings.IS_LOCAL)
        super(MailingList, self).save(*args, **kwargs)


class Template(models.Model):
    resume = models.CharField(max_length=255, help_text=u"Résumé du mail", verbose_name=u"Résumé")
    shortcut = models.CharField(max_length=20, help_text=u"Raccourci utilisé en interne", verbose_name="Raccourci")
    subject = models.CharField(max_length=255, help_text="Sujet", verbose_name="Sujet")
    body = models.TextField(help_text="Corps du message", verbose_name="Corps")

    def __unicode__(self):
        return self.resume

    class Meta:
        app_label = "notification"
