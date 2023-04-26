# coding: utf-8

# PYTHON IMPORTS
import os
import re

# DJANGO IMPORTS
from django import forms
from django.utils.translation import ugettext_lazy as _

# FILEBROWSER IMPORTS
from powercms.filebrowser.settings import FOLDER_REGEX, DIRECTORY, MEDIA_ROOT
from powercms.filebrowser.utils import convert_filename

ALNUM_NAME_RE = re.compile(FOLDER_REGEX, re.U)

# CHOICES
TRANSPOSE_CHOICES = (
    ("", "-----"),
    ("0", _("Flip horizontal")),
    ("1", _("Flip vertical")),
    ("2", _("Rotate 90° CW")),
    ("4", _("Rotate 90° CCW")),
    ("3", _("Rotate 180°")),
)


class CreateDirForm(forms.Form):
    """
    Form for creating a folder.
    """

    name = forms.CharField(widget=forms.TextInput(attrs=dict({'class': 'vTextField'}, max_length=50, min_length=3)), label=_('Name'), help_text=_('Only letters, numbers, underscores, spaces and hyphens are allowed.'), required=True)

    def __init__(self, path, *args, **kwargs):
        self.path = path
        self.site = kwargs.pop("filebrowser_site", None)
        super(CreateDirForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        "validate name"
        if self.cleaned_data['name']:
            # only letters, numbers, underscores, spaces and hyphens are allowed.
            if not ALNUM_NAME_RE.search(self.cleaned_data['name']):
                raise forms.ValidationError(_('Only letters, numbers, underscores, spaces and hyphens are allowed.'))
            # Folder must not already exist.
            if self.site.storage.isdir(os.path.join(self.path, convert_filename(self.cleaned_data['name']))):
                raise forms.ValidationError(_('The Folder already exists.'))
        return convert_filename(self.cleaned_data['name'])


class ChangeForm(forms.Form):
    """
    Form for renaming a file/folder.
    """

    custom_action = forms.ChoiceField(label=_('Actions'), required=False)
    path_to = forms.ChoiceField(label='Para', required=False)
    name = forms.CharField(widget=forms.TextInput(attrs=dict({'class': 'vTextField'}, max_length=50, min_length=3)), label=_('Name'), help_text=_('Only letters, numbers, underscores, spaces and hyphens are allowed.'), required=True)
    file = forms.CharField(widget=forms.TextInput(attrs=dict({'class': 'vLargeTextField'})), label=_('Arquivo'), required=False)

    def __init__(self, *args, **kwargs):
        self.path = kwargs.pop("path", None)
        self.fileobject = kwargs.pop("fileobject", None)
        self.site = kwargs.pop("filebrowser_site", None)
        super(ChangeForm, self).__init__(*args, **kwargs)

        # Initialize choices of custom action
        custom_action_choices = [("", "-----")]
        for name, action in self.site.applicable_actions(self.fileobject):
            custom_action_choices.append((name, action.short_description))
        self.fields['custom_action'].choices = custom_action_choices
        # Initialize choices of path_to
        path_to_choices = [("", "-----")]
        FULL_DIRECTORY = os.path.join(MEDIA_ROOT, DIRECTORY)
        for path in os.walk(FULL_DIRECTORY):
            path_to_choices.append((path[0], path[0].replace(FULL_DIRECTORY, '/')))
        self.fields['path_to'].choices = path_to_choices


    def clean_name(self):
        "validate name"
        if self.cleaned_data['name']:
            # only letters, numbers, underscores, spaces and hyphens are allowed.
            if not ALNUM_NAME_RE.search(self.cleaned_data['name']):
                raise forms.ValidationError(_('Only letters, numbers, underscores, spaces and hyphens are allowed.'))
            #  folder/file must not already exist.
            if self.site.storage.isdir(os.path.join(self.path, convert_filename(self.cleaned_data['name']))) and os.path.join(self.path, convert_filename(self.cleaned_data['name'])) != self.fileobject.path:
                raise forms.ValidationError(_('The Folder already exists.'))
            elif self.site.storage.isfile(os.path.join(self.path, convert_filename(self.cleaned_data['name']))) and os.path.join(self.path, convert_filename(self.cleaned_data['name'])) != self.fileobject.path:
                raise forms.ValidationError(_('The File already exists.'))
        return convert_filename(self.cleaned_data['name'])
