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
        return self.request.user.is_authenticated and self.request.user.id == house.creator.id
