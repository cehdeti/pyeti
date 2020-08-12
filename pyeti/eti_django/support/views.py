import django
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from .forms import SupportForm


class SupportView(SuccessMessageMixin, FormView):
    form_class = SupportForm
    template_name = 'eti_django/support/index.html'
    success_message = _('Your support request has been submitted. You should hear back from us shortly!')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        if self.__is_authenticated and hasattr(self.request.user, 'email'):
            initial['email'] = self.request.user.email
        return initial

    def get_success_url(self):
        return self.request.build_absolute_uri()

    @property
    def __is_authenticated(self):
        """
        https://docs.djangoproject.com/en/2.2/releases/1.10/#using-user-is-authenticated-and-user-is-anonymous-as-methods
        """
        if django.VERSION < (1, 10):
            return self.request.user.is_authenticated()
        return self.request.user.is_authenticated
