from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    DeleteView,
    UpdateView,
)
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import House
from .mixins import CreatorCheckMixin


class HomePageView(TemplateView):
    template_name = 'home.html'


class HouseListView(LoginRequiredMixin, ListView):
    model = House

    def get_queryset(self):
        return House.objects.filter(
            creator=self.request.user
        )


class HouseCreateView(LoginRequiredMixin, CreateView):
    model = House
    fields = ['name', 'creator']
    success_url = reverse_lazy('house_list')
    template_name_suffix = '_create_form'

    def post(self, request, *args, **kwargs):
        post = request.POST.copy()
        post['creator'] = request.user.id
        request.POST = post
        return super(HouseCreateView, self).post(request, *args, **kwargs)


class HouseDetailView(CreatorCheckMixin, DetailView):
    model = House


class HouseDeleteView(CreatorCheckMixin, DeleteView):
    model = House
    success_url = reverse_lazy('house_list')


class HouseUpdateView(CreatorCheckMixin, UpdateView):
    model = House
    fields = ['name']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        obj = self.get_object()
        return reverse_lazy('house_detail', args=(obj.id,))
