from django.conf import settings
import os


class TemplateConfig:
    def __init__(self, **kwargs):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """
        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        kwargs['template_name'] = self.get_template()

        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_template(self):
        themedir = os.path.join(settings.PROJECT_DIR, 'theme')
        templates = os.path.join(themedir, 'templates')
        tema_template = os.path.join(templates, 'cadastro.html')
        if not os.path.exists(tema_template):
            return 'crm/cadastro.html'
        return tema_template
