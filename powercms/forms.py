# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm, AuthenticationForm
from django.contrib.auth.models import User
from django.template import loader

from powercms.cms.email import sendmail


class EmailValidationOnForgotPassword(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = "Não existe nenhum usuário com esse email."
            self.add_error('email', msg)
        return email

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        # body = loader.render_to_string(email_template_name, context)
        link = '%s://%s/admin/reset/%s/%s/' %(context['protocol'], context['domain'], context['uid'], context['token'])
        sendmail(
            subject=subject,
            to=[to_email],
            params={'site_name': settings.SITE_NAME, 'link': link, 'nome': context['user']},
            template='reset.html',
        )

        # email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        # if html_email_template_name is not None:
        #     html_email = loader.render_to_string(html_email_template_name, context)
        #     email_message.attach_alternative(html_email, 'text/html')
        #
        # email_message.send()

class AuthenticationFormCustom(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            if '@' in username:
                user = User.objects.filter(email=username)
                if user.count() == 1:
                    username = user.get()

            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data