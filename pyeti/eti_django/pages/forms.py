from django import forms
from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from .models import Placeholder
from .utils import get_placeholders


def get_content_widget():
    class_ = getattr(
        settings,
        'PYETI_PAGES_CONTENT_WIDGET',
        'django.contrib.admin.widgets.AdminTextareaWidget'
    )
    return import_string(class_)


class PlaceholderForm(forms.ModelForm):

    name = forms.ChoiceField(choices=[])
    langcode = forms.ChoiceField(label=_('Language'), choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].choices = [(p, p) for p in sorted(get_placeholders())]
        self.fields['langcode'].choices = settings.LANGUAGES
        self.fields['langcode'].initial = settings.LANGUAGE_CODE

    class Meta:
        model = Placeholder
        fields = ('name', 'langcode', 'content',)
        widgets = {
            'content': get_content_widget(),
        }
