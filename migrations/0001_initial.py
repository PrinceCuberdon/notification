# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MailingList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation', models.DateField(auto_now=True)),
                ('subject', models.CharField(help_text=b'Sujet du message', max_length=150, verbose_name=b'Sujet')),
                ('content', models.TextField(help_text=b'Corps du message.', verbose_name=b'Message')),
                ('send_to_all', models.BooleanField(default=False, help_text='Envoyer le message \xe0 tous les utilisateurs inscripts', verbose_name='Envoyer \xe0 tous')),
                ('send_to_inactive', models.BooleanField(default=False, help_text='Envoyer le message \xe0 tous les utilisateurs qui ne participent pas', verbose_name='Envoyer aux inactifs')),
            ],
        ),
        migrations.CreateModel(
            name='Preference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Nom du serveur', max_length=40, verbose_name='Nom')),
                ('webmaster', models.EmailField(help_text='Adresse mail du webmaster', max_length=254, blank=True)),
                ('sendmail', models.EmailField(help_text="Email par default pour l'envoi d'email", max_length=254, verbose_name='Email')),
                ('anonymous', models.BooleanField(default=False)),
                ('username', models.CharField(help_text="Nom d'utilisateur", max_length=40, null=True, verbose_name='Utilisateur', blank=True)),
                ('password', models.CharField(help_text='Mot de passe', max_length=40, null=True, verbose_name=b'Mot de passe', blank=True)),
                ('server', models.CharField(help_text='Adresse du serveur', max_length=255, verbose_name=b'Serveur')),
                ('port', models.IntegerField(default=25, help_text='Port du serveur')),
                ('default_account', models.BooleanField(default=False, help_text='Serveur par d\xe9faut', verbose_name='Compte par d\xe9faut')),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resume', models.CharField(help_text='R\xe9sum\xe9 du mail', max_length=255, verbose_name='R\xe9sum\xe9')),
                ('shortcut', models.CharField(help_text='Raccourci utilis\xe9 en interne', max_length=20, verbose_name=b'Raccourci')),
                ('subject', models.CharField(help_text=b'Sujet', max_length=255, verbose_name=b'Sujet')),
                ('body', models.TextField(help_text=b'Corps du message', verbose_name=b'Corps')),
            ],
        ),
    ]
