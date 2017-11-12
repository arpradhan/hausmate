from django.contrib.auth import forms
from django.contrib.auth import get_user_model
from django.views.generic import CreateView
from django.urls import reverse_lazy


class UserCreationForm(forms.UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username",)
        field_classes = {'username': forms.UsernameField}


class UserCreateView(CreateView):
    model = get_user_model()
    form_class = UserCreationForm
    success_url = reverse_lazy('house_list')
