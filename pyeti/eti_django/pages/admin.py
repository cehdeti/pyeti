from django.contrib import admin
from django.utils.translation import get_language_info, ugettext as _

from .forms import PlaceholderForm
from .models import Placeholder


class LanguagesFieldListFilter(admin.AllValuesFieldListFilter):

    def choices(self, changelist):
        yield {
            'selected': self.lookup_val is None and self.lookup_val_isnull is None,
            'query_string': changelist.get_query_string(remove=[self.lookup_kwarg, self.lookup_kwarg_isnull]),
            'display': _('All'),
        }
        include_none = False
        for val in self.lookup_choices:
            if val is None:
                include_none = True
                continue
            display = get_language_info(val)['name_translated']
            yield {
                'selected': self.lookup_val == val,
                'query_string': changelist.get_query_string({self.lookup_kwarg: val}, [self.lookup_kwarg_isnull]),
                'display': display,
            }
        if include_none:
            yield {
                'selected': bool(self.lookup_val_isnull),
                'query_string': changelist.get_query_string({self.lookup_kwarg_isnull: 'True'}, [self.lookup_kwarg]),
                'display': self.empty_value_display,
            }


@admin.register(Placeholder)
class PlaceholderAdmin(admin.ModelAdmin):
    model = Placeholder
    list_display = ('name', 'language')
    list_filter = (
        ('langcode', LanguagesFieldListFilter),
    )
    search_fields = ('name',)
    form = PlaceholderForm

    def language(self, obj):
        return get_language_info(obj.langcode)['name_translated']
    language.short_description = 'Language'
