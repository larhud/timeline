from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from powercms.filebrowser.sites import site
from powercms.forms import AuthenticationFormCustom, EmailValidationOnForgotPassword

admin.autodiscover()

urlpatterns = [
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('admin/', admin.site.urls),
    path('chaining', include('smart_selects.urls')),

    path('admin/password_reset/', auth_views.PasswordResetView.as_view(form_class=EmailValidationOnForgotPassword),
         name='admin_password_reset'),
    path('admin_tools/', include('admin_tools.urls')),
    path('admin/filebrowser/', site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
admin.autodiscover()

urlpatterns += [
    # CMS
    path('', include('crm.urls')),
    path('', include('cms.urls')),
    path('chaining/', include('smart_selects.urls')),
    path('tppc/', include('dj_tppc.urls')),

]
admin.site.login_form = AuthenticationFormCustom
handler500 = 'cms.views.handler500'
handler404 = 'cms.views.page_not_found_view'
