# -*- coding: UTF-8 -*-
# notification is part of Band Cochon
# Band Cochon (c) Prince Cuberdon 2011 and Later <princecuberdon@bandcochon.fr>

import logging

from django import template
from django.conf import settings
from django.core.mail import send_mail
from libs.notification.models import Template

L = logging.getLogger("notification")


def notification_send(template_shortcut, dest=None, context=None):
    """
    Send an email based on a shortcut
    """
    if settings.IS_LOCAL:
        return True

    try:
        notif = Notification(template_shortcut)
        notif.push(dest, context)
        notif.send()

        return True

    except Exception as error:
        L.error(u"notification.notification_send : {error}".format(error=error))

    return False


class NotificationError(Exception):
    pass


class Notification(object):
    def __init__(self, template_shortcut=None):

        self.notif = []
        self.shortcut = template_shortcut

        self.subject = None
        self.body = None

    def push(self, dest, context=None, shortcut=None):
        """ Push notifications in a stack """
        sc = shortcut if shortcut is not None else self.shortcut

        if sc is None:
            if self.subject is None or self.body is None:
                L.error("notification.Notification.push: "
                        "Subject or body not set")
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

    def send(self):
        """
        Send all mails pushed.
        Do nothing on debug mode
        """
        for notif in self.notif:
            send_mail(subject=notif['subject'],
                      recipient_list=[notif['dest']],
                      message=notif['body'],
                      html_message='<html><body>%s</body></html>' %
                                   notif['body'],
                      from_email=settings.EMAIL_SENDER,
                      fail_silently=True)

    def render_template(self, template_shortcut, context):

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
