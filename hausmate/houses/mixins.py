from django.contrib.auth.mixins import UserPassesTestMixin

from .models import House


class CreatorCheckMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.creator == self.request.user


class HouseChildrenMixin(UserPassesTestMixin):
    def get_house(self):
        house_id = self.kwargs.get('house_id')
        return House.objects.get(id=house_id)

    def test_func(self):
        house = self.get_house()
        return self.request.user.id == house.creator.id

    def get_context_data(self):
        context_data = super().get_context_data()
        context_data['house_id'] = self.kwargs.get('house_id')
        return context_data
