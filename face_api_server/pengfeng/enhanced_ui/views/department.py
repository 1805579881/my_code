
import logging
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import  render
from rest.models import Person, Department
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib import messages

@method_decorator(login_required, name='dispatch')
class DepartmentListView(ListView):
    model = Department
    template_name = 'enhanced_ui/department_list.html'
    queryset = Department.objects.all()


@method_decorator(login_required, name='dispatch')
class DepartmentCreateView(CreateView):
    model = Department
    template_name = 'enhanced_ui/department_create.html'
    fields = ['name']

    def get_success_url(self):
        return reverse_lazy('enhanced_ui:department-list')


@method_decorator(login_required, name='dispatch')
class DepartmentUpdateView(UpdateView):
    model = Department
    template_name = 'enhanced_ui/department_update.html'
    fields = ['name']

    def get_success_url(self):
        return reverse_lazy('enhanced_ui:department-detail', kwargs={'pk': self.object.pk})


@method_decorator(login_required, name='dispatch')
class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'enhanced_ui/department_delete.html'
    success_url = reverse_lazy('enhanced_ui:department-list')

    def delete(self, *args, **kwargs):
        depart = Person.objects.filter(Q(is_deleted=False) & Q(department__pk=self.kwargs.get('pk')))
        if depart.count() >= 1:
            pk = self.kwargs.get('pk')
            messages.error(self.request, '此部门还有人员未删除，请先删除人员')
            return HttpResponseRedirect(reverse('enhanced_ui:department-delete', args=[(str(pk))]))
        else:
            department = Department.objects.get(pk=self.kwargs.get('pk'))
            department.is_deleted = True;
            department.save()
            return HttpResponseRedirect(reverse('enhanced_ui:department-list'))
            # super(Department, department).save(**kwargs)

@method_decorator(login_required, name='dispatch')
class DepartmentDetailView(DetailView):
    model = Department
    template_name = 'enhanced_ui/department_detail.html'


@csrf_exempt
@require_http_methods(["POST"])
def delete_selected_department(request):
    try:
        pks = request.POST.getlist('pks[]')
        with transaction.atomic():
            Department.objects.filter(id__in=pks).update(is_deleted=True)
        result = {'error': False}
    except Exception as e:
        result = {
            'error': True,
            'detail': str(e)
        }
    return JsonResponse(result)


@require_http_methods(["GET"])
def find_department_name(request):
    depart_name = request.GET.get("name")
    depart = Department.objects.filter(Q(name=depart_name) & Q(is_deleted=False))
    if depart.count() > 0:
        result = {
            'error': True,
            'status': 0
        }
        return JsonResponse(result)
    else:
        result = {
            'error': False,
            'status': 1
        }
        return JsonResponse(result)


@require_http_methods(["GET"])
def update_department_is_delete(request):
    depart_name = request.GET.get("name")
    depart = Department.objects.filter(name=depart_name)
    if depart.count() == 1:
        department = Department.objects.get(name=depart_name)

        if department.is_deleted:
            department.is_deleted = False
            department.save()
            result = {
                'error': False
            }
        else:
            result = {
                'error': False
            }
        return JsonResponse(result)
    else:
        result = {
            'error': True,
        }
        return JsonResponse(result)