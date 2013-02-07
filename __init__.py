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

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import sys
import os
import datetime

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.conf import settings
from django.core.validators import email_re

from notification.models import Preference, Template


def notification_send(template_shortcut, dest=None, context=None, account_name=None):
    """ Send an email based on a shortcut """
    pref = None
    try:
        if account_name is not None:
            pref= Preference.objects.get(name=account_name)
        else:
            pref = Preference.objects.get_default()
    except ObjectDoesNotExist:
        raise Http404()
            
    if dest is None:
        dest = pref.webmaster
    try:
        notif = Notification(template_shortcut)
        notif.push(dest, context)
        notif.send()
        
    except ObjectDoesNotExist:
        return False
    
    except smtplib.SMTPException as error:
        """ Can't send the email """
        ajax_log("notification.notification_send: %s" % error)
        return False
    
    except Exception as error:
        ajax_log("notification.notification_send : %s" % error)
    
    return True

class NotificationError(Exception):
    pass

class Notification(object):
    def __init__(self, template_shortcut=None, debug=False):
        self.notif = []
        self.shortcut = template_shortcut
        self.pref = Preference.objects.get_default()
        if debug == False:
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
        if shortcut is None:
            shortcut = self.shortcut
            
        if self.shortcut is None:
            if self.subject is None or self.body is None:
                raise NotificationError("Subject or body not set")
            subject = self.subject
            body = self.body
        else:
            subject, body = self.render_template(self.shortcut, context)
            
        self.notif.append({
            'subject' : subject,
            'body': body,
            'dest': dest
        })

    def send(self, debug=False):
        """ Send all mails pushed """
        if settings.IS_BETA or settings.IS_LOCAL:
            return

        for notif in self.notif:
            # Do HTML text mail
            msg = MIMEMultipart('alternative')
            msg['From'] = self.pref.sendmail
            msg['To'] = notif['dest']
            msg['Subject'] = notif['subject']
            #textpart = MIMEText(notif['body'],'plain', 'utf-8')
            htmlpart = MIMEText('<html><body>' + notif['body'] + '</body></html>', 'html', 'utf-8')
            msg.attach(htmlpart)
            #msg.attach(textpart)
                            
            if debug == False:
                if email_re.match(notif['dest']):
                    # Ensure email is a valid one
                    self.connection.sendmail(self.pref.sendmail, notif['dest'], msg.as_string())
            else:
                print msg.as_string()

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
 
def ajax_log(message, testing=False):
    """ Write a message for debugging ajax calls (Prefer this method over logging std call """
    message = "%s : %s" % (datetime.datetime.today(), message)
    open(os.path.join(settings.MEDIA_ROOT, "ajax_log.txt"), 'a').write("%s\n" % message)
    if (settings.DEBUG and settings.IS_LOCAL) and not testing:
        """ Write message on the default out put """
        print >> sys.stderr, message

    #if Preferences.objects.filter(default_accout=True)[0].send_to_admin == True:
    #    notification_send()

