# coding:utf-8
from django.contrib import admin
from poweradmin.admin import PowerModelAdmin

# Registrar as preferências do django admin tools
from admin_tools.dashboard.models import DashboardPreferences


class DashboardPreferencesAdmin(PowerModelAdmin):
    list_display = ('user', )
    list_filter = ('user', )


admin.site.register(DashboardPreferences, DashboardPreferencesAdmin)
