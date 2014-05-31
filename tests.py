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
"""
Test notification.

Embed its own fake smtpd server
"""
import os
#import datetime

from django.test import TestCase
from django.conf import settings
from django.http import Http404
from django.template import Context
from django.contrib.auth.models import User

from core.bandcochon.models import Utilisateur #, Picture, TownShip, Town, Place
from .models import Preference, Template, MailingList
from . import ajax_log, notification_send

class TestAjaxLog(TestCase):
    def setUp(self):
        """ Clean up the ajax_log.txt file """
        open(os.path.join(settings.MEDIA_ROOT, "ajax_log.txt"),"w").write('')
        
    def test_ajax_log(self):
        """ Write a message. """
        message = u"this is a test"
        ajax_log(message)
        content = open(os.path.join(settings.MEDIA_ROOT,"ajax_log.txt"), "r").read()
        self.assertIn(message, content)
        
class TestPreferenceModel(TestCase):
    def test_double_pref(self):
        self._create_pref()
        two = self._create_pref()
        self.assertEqual(two.pk, Preference.objects.get_default().pk)
    
    def test_double_pref_with_default(self):
        one = self._create_pref()
        two = self._create_pref()
        two.default_account = False
        two.save()
        self.assertEqual(one.pk, Preference.objects.get_default().pk)

    def test_password_offuscation(self):
        """ """
        pref = self._create_pref()
        self.assertEqual(pref.offuscate_pass(), u"*" * len(pref.password))
        
    def test_default2string(self):
        """ """
        pref = self._create_pref()
        self.assertEqual(pref.default2string(), u"Oui")
        pref.default_account = False
        pref.save()
        self.assertEqual(pref.default2string(), u"Non")
        
    def _create_pref(self):
        """ Create a dummy preference """
        return Preference.objects.create(
            name="test",
            webmaster="someone@exemple.com",
            sendmail="someone-else@example.com",
            anonymous=False,
            username="testme",
            password="testmeagain",
            server="localhost",
            port=1025,
            default_account=True
        )

class TestThatNeedServer(TestCase):
    pass
#    def setUp(self):
#        self.server = ThreadedServer()
#        self.server.start()
#        
#    def tearDown(self):
#        self.server.set_stop()
        
    
class TestNotificationSend(TestThatNeedServer):
    """ Test notification object and shortcut
    """
    def test_no_preferences_sets_no_template(self):
        """ Test with no template and no preferences. """
        with self.assertRaises(Http404):
            notification_send("atest")
        
    def _create_pref(self, name="test", webmaster="someone@example.com"):
        """ Create a dummy preference """
        Preference.objects.create(
            name=name,
            webmaster=webmaster,
            sendmail="someone-else@example.com",
            anonymous=True,
            server="localhost",
            port=1025,
            default_account=True
        )

    def _create_template(self):
        """ Create a dummy template """
        Template.objects.create(
            resume="a test",
            shortcut='atest',
            subject="a subject",
            body="A body {{ testme }}"
        )
        
    def test_preferences_sets_no_template(self):
        """ Test with wrong template name (not created in this case) """
        self._create_pref()
        self.assertFalse(notification_send("atest"))
            
    def test_preferences_sets_template(self):
        """ Send an email. """ 
        self._create_pref()
        self._create_template()
        self.assertTrue(notification_send("atest"))
    
    def test_with_dest(self):
        """ Test with a destinataire """
        self._create_pref()
        self._create_template()
        self.assertTrue(notification_send("atest", dest="hello@world.com"))
        
    def test_with_context(self):
        """ """
        self._create_pref()
        self._create_template()
        context = Context({ 'testme' : 'This is a test'})
        self.assertTrue(notification_send('atest', context=context))
        
    
    def test_account_name(self):
        """ Test multiple account """
        self._create_pref("first")
        self._create_pref("second", "somewhere@overtherainbow.com")
        self._create_template()
        self.assertTrue(notification_send('atest', account_name="second"))
        

class TestMailingList(TestThatNeedServer):
    def setUp(self):
        """ Create two users, mail preference and a template """
        Preference.objects.create(
            name="test",
            webmaster="me@myself.and.i",
            sendmail="someone-else@example.com",
            anonymous=True,
            server="localhost",
            port=1025,
            default_account=True
        )
        
        Template.objects.create(
            resume="a test",
            shortcut='atest',
            subject="a subject",
            body="A body {{ testme }}"
        )
        
        self.user1 = User.objects.create(username="user1", email="user1@user1.com")
        Utilisateur.objects.create(user=self.user1)
        user2 = User.objects.create(username="user2", email="user1@user2.com")
        Utilisateur.objects.create(user=user2)
        
        
    def test_send_to_nobody(self):
        """ Does nothing. Just saving """
        MailingList.objects.create(
            subject="This is a test",
            content="Helo ! This is a test {{ withvariable }}"
        )
        
    def test_send_to_all(self):
        """ Send to all users. Please take a look to Debug SMTPd server """
        MailingList.objects.create(
            subject="This is a test",
            content="Helo ! This is a test {{ withvariable }}",
            send_to_all=True
        )
        
    def test_send_to_inactive(self):
        """ Send to inactive """
        MailingList.objects.create(
            subject="This is a test",
            content="Helo ! This is a test {{ withvariable }}",
            send_to_inactive=True
        )        
        
    def test_send_to_active(self):
        """ Send to active users """
#        tship = TownShip.objects.create(name="testship")
#        town = Town.objects.create(name="testtown", township=tship, added_by=self.user1)
#        place = Place.objects.create(name="testplace", town=town, added_by=self.user1)
#        Picture.objects.create(user=self.user1,
#                               submission_date=datetime.datetime.now(),
#                               township=tship,
#                               town=town,
#                               place=place)
#        MailingList.objects.create(
#            subject="This is a test",
#            content="Helo ! This is a test {{ withvariable }}",
#            send_to_active=True
#        )


