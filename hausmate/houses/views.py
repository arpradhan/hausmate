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

from .models import House, Roommate, Bill, Payment, PaymentEvent
from .mixins import CreatorCheckMixin, HouseChildrenMixin


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
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        Roommate.objects.create(
            name=self.request.user.first_name,
            house=self.object
        )
        return super().form_valid(form)


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


class RoommateCreateView(HouseChildrenMixin, CreateView):
    model = Roommate
    fields = ['name', 'house']
    template_name_suffix = '_create_form'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        house = self.get_house()
        context_data['house_id'] = house.id
        return context_data

    def post(self, request, *args, **kwargs):
        post = request.POST.copy()
        post['house'] = self.get_house().id
        request.POST = post
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        house = self.get_house()
        return reverse_lazy('house_detail', args=(house.id,))


class BillCreateView(HouseChildrenMixin, CreateView):
    model = Bill
    fields = ['name', 'amount', 'owner', 'house']
    template_name_suffix = '_create_form'

    def form_valid(self, form):
        self.object = form.save()
        self.object.create_split_payments()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        house = self.get_house()
        roommates = house.roommate_set.values('id', 'name')
        context_data = super().get_context_data()
        context_data['house_id'] = house.id
        context_data['roommates'] = roommates
        return context_data

    def post(self, request, *args, **kwargs):
        post = request.POST.copy()
        post['house'] = self.get_house().id
        request.POST = post
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        house = self.get_house()
        return reverse_lazy('house_detail', args=(house.id,))


class BillDetailView(HouseChildrenMixin, DetailView):
    model = Bill

    def get_context_data(self, **kwargs):
        context_data = super(BillDetailView, self).get_context_data(**kwargs)
        payments = self.get_object().payment_set.all()
        context_data['payments'] = payments
        return context_data


class PaymentEventCreateView(CreateView):
    model = PaymentEvent
    fields = ['amount', 'payment']

    def post(self, request, *args, **kwargs):
        post = request.POST.copy()
        post['payment'] = self.get_payment().id
        request.POST = post
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        bill = self.get_payment().bill
        return reverse_lazy('bill_detail', args=(bill.house.id, bill.id,))

    def get_payment(self):
        payment_id = self.kwargs.get('payment_id')
        return Payment.objects.get(id=payment_id)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['payment_id'] = self.get_payment().id
        return context_data
