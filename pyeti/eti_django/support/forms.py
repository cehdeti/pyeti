from django import forms
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import ugettext_lazy as _


class SupportForm(forms.Form):

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
        data = self.cleaned_data
        email = EmailMessage(
            subject=data['subject'],
            body=data['message'],
            to=[settings.PYETI_SUPPORT_EMAIL],
            from_email=settings.DEFAULT_FROM_EMAIL,
            reply_to=[data['email']],
        )
        for file_ in self.files.getlist('files'):
            email.attach(file_.name, file_.read(), file_.content_type)
        email.send()
