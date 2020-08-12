import logging

import requests
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class SupportForm(forms.Form):
    """
    Form that creates tickets in Freshdesk.

    Uses the following settings:
        - `PYETI_SUPPORT_FRESHDESK_SUBDOMAIN`
        - `PYETI_SUPPORT_FRESHDESK_API_KEY`
        - `PYETI_SUPPORT_FRESHDESK_PRODUCT_ID` (optional)
    """

    email = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
    files = forms.FileField(label=_('File(s)'), widget=forms.FileInput(attrs={'multiple': True}), required=False)

    # Honeypot field
    phonenumber = forms.CharField(required=False)

    def clean(self):
        data = super().clean()
        if not data['phonenumber']:
            return data
        raise forms.ValidationError(_('Please do not fill in the "phonenumber" field'))

    def save(self):
        response = self.__do_request(*self.__build_payload())

        if response:
            response.raise_for_status()

    def __build_payload(self):
        data = self.cleaned_data

        payload = {
            'email': data['email'],
            'subject': data['subject'],
            'description': data['message'],
            'status': 2,
            'priority': 1,
        }

        product_id = getattr(settings, 'PYETI_SUPPORT_FRESHDESK_PRODUCT_ID', None)
        if product_id:
            payload['product_id'] = int(product_id)

        if hasattr(self.files, 'getlist'):
            files = [
                ('attachments[]', (file_.name, file_, file_.content_type))
                for file_ in self.files.getlist('files')
            ]
        else:
            files = []

        return payload, files

    def __do_request(self, data, files):
        freshdesk_subdomain = getattr(settings, 'PYETI_SUPPORT_FRESHDESK_SUBDOMAIN', None)
        freshdesk_api_key = getattr(settings, 'PYETI_SUPPORT_FRESHDESK_API_KEY', None)

        if not freshdesk_subdomain or not freshdesk_api_key:
            logger.info("""
                Received support submission, but API URL and/or key are not
                set up. Here is the data:
                Payload: %s
                Files: %s
                """ % (data, files))
            return

        if len(files) == 0:
            return requests.post(
                'https://%s.freshdesk.com/api/v2/tickets' % freshdesk_subdomain,
                auth=(freshdesk_api_key, 'x'),
                json=data,
            )
        else:
            return requests.post(
                'https://%s.freshdesk.com/api/v2/tickets' % freshdesk_subdomain,
                auth=(freshdesk_api_key, 'x'),
                data=data,
                files=files,
            )
