# -*- coding: UTF-8 -*-
# notification is part of Band Cochon
# Band Cochon (c) Prince Cuberdon 2011 and Later <princecuberdon@bandcochon.fr>

"""
Test notification.

Embed its own fake smtpd server
"""
import smtplib

from django.test import TestCase
from django.http import Http404
from django.template import Context
from django.contrib.auth.models import User
import minimock

from core.bandcochon.models import Utilisateur
from .models import Preference, Template, MailingList
from . import notification_send


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
    def setUp(self):
        """ Mock the smtp library to control the email sending
        """
        smtplib.SMTP = minimock.Mock('smtplib.SMTP', tracker=None)
        smtplib.SMTP.mock_returns = minimock.Mock('smtp_connection', tracker=None)


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
        context = Context({'testme': 'This is a test'})
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

        super(TestMailingList, self).setUp()

    def test_send_to_nobody(self):
        """ Does nothing. Just saving """
        MailingList.objects.create(
            subject="This is a test",
            content="Helo ! This is a test {{ withvariable }}"
        )

    def test_send_to_all(self):
        """ Send to all users """
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
