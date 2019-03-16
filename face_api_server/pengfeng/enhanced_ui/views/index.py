from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth import logout
from django.contrib.auth.views import PasswordChangeView
from rest.models import Person,Department,Record
from sync.models import Device


@method_decorator(login_required, name='dispatch')
class IndexRedirectView(RedirectView):
    url = reverse_lazy('enhanced_ui:face-list')


@method_decorator(login_required, name='dispatch')
class LogoutView(RedirectView):
    url = reverse_lazy('enhanced_ui:index')

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return super(LogoutView, self).get_redirect_url(*args, **kwargs)


@method_decorator(login_required, name='dispatch')
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'enhanced_ui/change_password.html'
    success_url = reverse_lazy('enhanced_ui:logout')


@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = 'enhanced_ui/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        people = Person.objects.filter(is_deleted=False)
        context['people_count'] = people.count()
        departs = Department.objects.filter(is_deleted=False)
        context['depart_count'] = departs.count()
        records = Record.objects.count()
        context['record_count'] = records
        devices = Device.objects.count()
        context['device_count'] = devices
        return context
