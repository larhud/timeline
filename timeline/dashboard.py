# -*- coding: utf-8 -*-
"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'dashboard.CustomAppIndexDashboard'
"""

from admin_tools.dashboard import modules
from admin_tools.utils import get_admin_site_name

from powercms.dashboard import CustomIndexDashboard, AppIndexDashboard


class CustomIndexDashboardVepeInfo(CustomIndexDashboard):
    """
    Custom index dashboard for base-tools.
    """
    title = ''
    columns = 2

    def init_with_context(self, context):
        super().init_with_context(context)

        site_name = get_admin_site_name(context)
        request = context['request']

        self.children += [
            modules.ModelList(
                u'Base de Notícias',
                models=('base.models.*',),
            ),
        ]


class CustomAppIndexDashboardVepeInfo(AppIndexDashboard):
    """
    Custom app index dashboard for base-tools.
    """

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(self.app_title, self.models),
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboardVepeInfo, self).init_with_context(context)
