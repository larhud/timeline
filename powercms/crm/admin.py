# -*- coding: utf-8 -*-
from django.contrib import admin
from django.http import HttpResponse

from poweradmin.admin import PowerModelAdmin
from .models import Contato


class ContatoAdmin(PowerModelAdmin):
    list_display = ('nome', 'email', 'status_email')
    actions = ('export_csv', )

    def export_csv(self, request, queryset):
        csv = ""
        for q in queryset:
            csv += '"%(nome)s";"%(email)s"\n' % {'nome': q.nome, 'email': q.email, }
        response = HttpResponse(csv, mimetype='application/csv; charset=utf-8', )
        response['Content-Disposition'] = 'filename=contatos.csv'
        return response
    export_csv.short_description = "Gerar arquivo de exportação"


admin.site.register(Contato, ContatoAdmin)
