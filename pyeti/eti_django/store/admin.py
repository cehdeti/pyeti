from django.contrib import admin
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from pyeti.eti_django.store.models import UsageLicense


class UsageLicenseStatusFilter(admin.SimpleListFilter):
    STATUSES = [
        ('1', _('Active')),
        ('0', _('Expired')),
    ]

    title = _('status')
    parameter_name = 'status'

    def lookups(self, *args, **kwargs):
        return self.STATUSES

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.active()
        if self.value() == '0':
            return queryset.expired()
        return queryset


@admin.register(UsageLicense)
class UsageLicenseAdmin(admin.ModelAdmin):
    model = UsageLicense
    actions = None
    list_display = ('token', 'num_seats', 'start_date', 'end_date', 'order_number')
    list_display_links = None
    list_filter = (UsageLicenseStatusFilter,)
    search_fields = ('token',)

    def order_number(self, obj):
        if not obj.spree_order_number:
            return
        store_host = getattr(settings, 'PYETI_STORE_URL', None)
        if store_host is None:
            return obj.spree_order_number
        return format_html(
            '<a target="_blank" href="{}">{}</a>',
            '%sadmin/orders/%s/edit' % (store_host, obj.spree_order_number),
            obj.spree_order_number
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def change_view(request, object_id, form_url='', extra_context=None):
        """
        We want to disallow editing usage licenses, but we can't just override
        `has_change_permission` and return `False` because that's how django
        controls access to the listing page also. So we'll just disable all
        links to the edit page and raise an exception here in case anyone gets
        here by mistake.
        """
        raise PermissionDenied('Usage licenses cannot be edited')
