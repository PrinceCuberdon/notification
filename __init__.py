# -*- coding: UTF-8 -*-
# notification is part of Band Cochon
# Band Cochon (c) Prince Cuberdon 2011 and Later <princecuberdon@bandcochon.fr>


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.conf import settings
from django.core.validators import validate_email, ValidationError

L = logging.getLogger("notification")


def notification_send(template_shortcut, dest=None, context=None, account_name=None):
    """ Send an email based on a shortcut """
    from .models import Preference

    try:
        if account_name is not None:
            pref = Preference.objects.get(name=account_name)
        else:
            pref = Preference.objects.get_default()

    except ObjectDoesNotExist:
        L.error(u"notification.notification_send: The account_name '{name}' is not found".format(name=account_name))
        raise Http404()

    if dest is None:
        dest = pref.webmaster
    try:
        notif = Notification(template_shortcut)
        notif.push(dest, context)
        notif.send()

        return True

    except ObjectDoesNotExist as error:
        L.error(u"notification.notification_send: {error}".format(error=error))

    except smtplib.SMTPException as error:
        """ Can't send the email """
        L.error(u"notification.notification_send: {error}".format(error=error))

    except Exception as error:
        L.error(u"notification.notification_send : {error}".format(error=error))

    return False


class NotificationError(Exception):
    pass


class Notification(object):
    def __init__(self, template_shortcut=None, debug=False):
        from .models import Preference

        self.notif = []
        self.shortcut = template_shortcut
        self.pref = Preference.objects.get_default()
        if not debug:
            self.connection = smtplib.SMTP(self.pref.server, int(self.pref.port))
            if not self.pref.anonymous:
                self.connection.login(self.pref.username, self.pref.password)
            else:
                self.connection.helo()
        else:
            self.connection = None

        self.subject = None
        self.body = None

    def __del__(self):
        try:
            self.connection.quit()
        except AttributeError:
            pass

    def push(self, dest, context=None, shortcut=None):
        """ Push notifications in a stack """
        sc = shortcut if shortcut is not None else self.shortcut

        if sc is None:
            if self.subject is None or self.body is None:
                L.error("notification.Notification.push: Subject or body not set")
                raise NotificationError("Subject or body not set")

            subject = self.subject
            body = self.body
        else:
            subject, body = self.render_template(sc, context)

        self.notif.append({
            'subject': subject,
            'body': body,
            'dest': dest
        })

    def send(self, debug=False):
        """
        Send all mails pushed.
        Do nothing on debug mode
        """
        if settings.IS_LOCAL or debug:
            return

        for notif in self.notif:
            # Do HTML text mail
            msg = MIMEMultipart('alternative')
            msg['From'] = self.pref.sendmail
            msg['To'] = notif['dest']
            msg['Subject'] = notif['subject']
            htmlpart = MIMEText('<html><body>' + notif['body'] + '</body></html>', 'html', 'utf-8')
            msg.attach(htmlpart)

            if not debug:
                try:
                    # Ensure email is a valid one
                    validate_email(notif['dest'])
                    self.connection.sendmail(self.pref.sendmail, notif['dest'], msg.as_string())
                except ValidationError as e:
                    L.error(u"notification.Notification.send: Unable to send a emain. Reasons: {error}".format(error=e))

    def render_template(self, template_shortcut, context):
        from .models import Template

        temp = Template.objects.get(shortcut=template_shortcut)
        body = u"%s" % temp.body
        subject = u"%s" % temp.subject
        if context is not None:
            subject = template.Template(subject).render(context)
            body = template.Template(body).render(context)

        return subject, body

    def set_content(self, subject, body):
        """ Set the content mail directly (no templates)
        @see MailingList model """
        self.subject = subject
        self.body = body
