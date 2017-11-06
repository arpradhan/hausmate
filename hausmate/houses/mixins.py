from django.contrib.auth.mixins import UserPassesTestMixin


class CreatorCheckMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.creator == self.request.user
