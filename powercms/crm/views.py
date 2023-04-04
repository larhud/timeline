# coding: utf-8
from django.contrib import messages
from django.views.generic import FormView

from .forms import ContatoForm
from .models import Contato
from .templates_config import TemplateConfig


class ContatoView(TemplateConfig, FormView):
    form_class = ContatoForm
    template_name = 'crm/cadastro.html'

    def get_context_data(self, **kwargs):
        context = super(ContatoView, self).get_context_data(**kwargs)
        context['title'] = 'Contato'
        return context

    def form_valid(self, form):
        Contato.objects.get_or_create(
            email=form.cleaned_data.get('email'),
            defaults={'nome': form.cleaned_data.get('nome')}
        )
        form.sendemail()

        messages.info(self.request, u'Contato cadastrado com sucesso!')
        form = self.form_class()

        return self.response_class(
            request=self.request,
            template=self.template_name,
            context=self.get_context_data(form=form),
        )
