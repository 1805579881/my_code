# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView,View
from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse
from django.db.models import Q
from models import PeopleInfo
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils import  timezone
import base64
import json
# Create your views here.


# @method_decorator(login_required, name='dispatch')
class PeopleIndex(ListView):
    model = PeopleInfo
    template_name = 'info_management_index.html'
    queryset = PeopleInfo.objects.filter()


# @method_decorator(login_required, name='dispatch')
class PeopleCreate(CreateView):
    model = PeopleInfo
    template_name = 'people_info_create.html'
    fields = ['name','number','image']

    def get_success_url(self):
        return reverse_lazy('info_management:info_management_index')

class PeopleDemo(ListView):
    model = PeopleInfo
    template_name = 'demo.html'
    queryset = PeopleInfo.objects.filter()

# class PeopleInfoEditView(UpdateView):
#     model = PeopleInfo
#     template_name = 'people_info_edit.html'
#     fields = ['name','number','image']
#
#     def get_success_url(self):
#         return reverse_lazy('info_management_detail' ,kwargs={'pk': self.object.pk})
#
#
# class PeopleInfoDetailView(DetailView):
#     model = PeopleInfo
#     template_name = 'people_info_detail.html'
#
#     def get_context_data(self, **kwargs):
#         kwargs["obj_list"] = self.model.objects.all()
#         return super(self.__class__, self).get_context_data(**kwargs)
#
#
# class PeopleInfoDeleteView(DeleteView):
#     model = PeopleInfo
#     template_name = ''
#     success_url = reverse_lazy('info_management_index')

def delete(request):
    if request.method == "DELETE":
        pk_list = request.Delete.get("pk_list",None)
        for i in pk_list:
            PeopleInfo.objects.filter(pk=i).delete()
        return redirect('index/',message ="删除成功")

def edit_info(request):
    if request.method == "GET":
        pk = request.GET.get('pk',None)
        people_obj = PeopleInfo.objects.filter(pk=pk)
        return render(request, 'people_info_edit.html',{'people_obj':people_obj})
    elif request.method == 'POST':
        pk = request.POST.get("pk", None)
        name = request.POST.get('name',None)
        number = request.POST.get('number', None)
        image = request.FILES.get("image",None)
        if not pk:
            return JsonResponse({"error":"未获取信息的ID，请刷新页面重试"})
        if not name:
            return HttpResponse("未获取信息的姓名，姓名为必填项，请刷新页面重试")
        if not number:
            return HttpResponse("未获取信息的工号，工号为必填项，请刷新页面重试")
        if not image:
            return HttpResponse("未获取带上传的照片，照片为必填项，请刷新页面重试")
        people_obj = PeopleInfo.objects.filter(pk=pk)
        if people_obj:
            image_str = image.read()
            image_base64 = base64.b64encode(image_str)
            print image_base64
            is_update = people_obj.update(name=name,number=number,image=image,image_base64=image_base64)
            if is_update:
                return redirect('info_management:info_management_index')
            else:
                return HttpResponse("数据库错误，修改数据失败")
        else:
            return HttpResponse("ID值错误，请刷新页面重试")

def detail_info(request):
    if request.method == "GET":
        pk = request.GET.get("pk", None)
        if pk:
            people_obj = PeopleInfo.objects.filter(pk=pk)
            return render(request, "people_info_detail.html", {'people_info': people_obj})
        else:
            return HttpResponse("未获取到要修改用户ID，请刷新页面重试")


def delete_info(request):
    if request.method == "GET":
        pk = request.GET.get("pk", None)
        if pk:
            people_obj = PeopleInfo.objects.filter(pk=pk)
            return render(request,"people_info_delete.html", {"people_info":people_obj})
        else:
            return HttpResponse("未获取到要删除用户的ID，请刷新页面重试")
    elif request.method == "POST":
        pk = request.POST.get('pk',None)
        print "请求进来", pk
        if pk:
            is_delete = PeopleInfo.objects.filter(pk=pk).delete()
            if is_delete:
                return redirect('info_management:info_management_index')
            else:
                return HttpResponse("数据库删除数据失败，请稍后重试")
        else:
            return render(request, "people_info_delete.html", {"error":"未获取到要删除用户的ID，请刷新页面重试"})

