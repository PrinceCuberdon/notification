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
import minimock

from .models import Template
from . import notification_send


class TestThatNeedServer(TestCase):
    def setUp(self):
        """ Mock the smtp library to control the email sending
        """
        smtplib.SMTP = minimock.Mock('smtplib.SMTP', tracker=None)
        smtplib.SMTP.mock_returns = minimock.Mock('smtp_connection',
                                                  tracker=None)


class TestNotificationSend(TestThatNeedServer):
    """ Test notification object and shortcut
    """

    def test_no_preferences_sets_no_template(self):
        """ Test with no template and no preferences. """
        with self.assertRaises(Http404):
            notification_send("atest")

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
        self.assertFalse(notification_send("atest"))

    def test_preferences_sets_template(self):
        """ Send an email. """
        self._create_template()
        self.assertTrue(notification_send("atest"))

    def test_with_dest(self):
        """ Test with a destinataire """
        self._create_template()
        self.assertTrue(notification_send("atest", dest="hello@world.com"))

    def test_with_context(self):
        """ """
        self._create_template()
        context = Context({'testme': 'This is a test'})
        self.assertTrue(notification_send('atest', context=context))

    def test_account_name(self):
        """ Test multiple account """
        self._create_template()
        self.assertTrue(notification_send('atest',))

