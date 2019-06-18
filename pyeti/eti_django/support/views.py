from django.views.generic import FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext_lazy as _

from .forms import SupportForm


class SupportView(SuccessMessageMixin, FormView):
    form_class = SupportForm
    template_name = 'eti_django/support/index.html'
    success_message = _('Your support request has been submitted. You should hear back from us shortly!')

    def is_authenticated(user):
        if callable(user.is_authenticated):
            return user.is_authenticated()
        return user.is_authenticated

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        if self.is_authenticated(self.request.user) and hasattr(self.request.user, 'email'):
            initial['email'] = self.request.user.email
        return initial

    def get_success_url(self):
        return self.request.build_absolute_uri()
