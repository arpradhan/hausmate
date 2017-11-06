from faker import Faker

from django.test import TestCase
from django.urls import reverse
from django.http.response import HttpResponseRedirect, HttpResponse

from core import factories

from houses.models import House, Roommate

fake = Faker()


class AnonUserVisitsCreateHouse(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse('house_create'))

    def test_user_is_redirected(self):
        self.assertEqual(self.response.status_code, HttpResponseRedirect.status_code)


class AnonUserCreatesHouse(TestCase):
    def setUp(self):
        data = {'name': fake.address()}
        self.response = self.client.post(reverse('house_create'), data=data)

    def test_user_is_redirected(self):
        self.assertEqual(self.response.status_code, HttpResponseRedirect.status_code)

    def test_house_is_not_created(self):
        self.assertEqual(House.objects.count(), 0)


class UserCreatesHouse(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = factories.create_fake_user()

    def setUp(self):
        data = {'name': fake.address()}
        self.client.force_login(user=self.user)
        self.response = self.client.post(reverse('house_create'), data=data)

    def test_house_is_created(self):
        self.assertEqual(House.objects.count(), 1)

    def test_user_is_redirected_to_house_list(self):
        self.assertEqual(
            self.response.status_code,
            HttpResponseRedirect.status_code)
        self.assertEqual(self.response.url, reverse('house_list'))

    def test_house_creator(self):
        house = House.objects.first()
        self.assertIsNotNone(house.creator)
        self.assertEqual(house.creator.id, self.user.id)


class UserVisitsHouseList(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = factories.create_fake_user()
        House.objects.create(
            name=fake.address(),
            creator=cls.user
        )
        House.objects.create(
            name=fake.address(),
            creator=factories.create_fake_user(),
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.response = self.client.get(reverse('house_list'))

    def test_list_houses_created_by_user(self):
        queryset = self.response.context['object_list']
        self.assertEqual(queryset.count(), 1)
        creator = queryset.first().creator
        self.assertEqual(self.user.id, creator.id)


class AnonUserVisitsHouse(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.house = House.objects.create(
            name=fake.address(),
            creator=factories.create_fake_user(),
        )

    def setUp(self):
        self.response = self.client.get(
            reverse('house_detail', args=(self.house.id,))
        )

    def test_user_is_redirected(self):
        self.assertEqual(self.response.status_code, HttpResponseRedirect.status_code)


class UserVisitsHouse(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = factories.create_fake_user()
        cls.house = House.objects.create(
            creator=cls.user,
            name=fake.address(),
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.response = self.client.get(
            reverse('house_detail', args=(self.house.id,))
        )

    def test_user_can_view_house(self):
        self.assertEqual(self.response.status_code, HttpResponse.status_code)


class AnonUserDeletesHouse(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = factories.create_fake_user()
        cls.house = House.objects.create(
            creator=cls.user,
            name=fake.address(),
        )

    def setUp(self):
        self.response = self.client.post(
            reverse('house_delete', args=(self.house.id,))
        )

    def test_user_is_redirected(self):
        self.assertEqual(self.response.status_code, HttpResponseRedirect.status_code)

    def test_house_is_not_deleted(self):
        self.assertEqual(
            House.objects.first().creator.id,
            self.user.id,
        )


class TestAnonUserUpdatesHouse(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.name = fake.address()
        cls.house = House.objects.create(
            creator=factories.create_fake_user(),
            name=cls.name,
        )

    def setUp(self):
        data = {'name': fake.address()}
        self.response = self.client.post(
            reverse('house_update', args=(self.house.id,)),
            data=data,
        )

    def test_house_is_not_edited(self):
        house = House.objects.get(id=self.house.id)
        self.assertEqual(house.name, self.name)

    def test_user_is_redirected(self):
        self.assertEqual(self.response.status_code, HttpResponseRedirect.status_code)


class UserVisitsUpdateHouse(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = factories.create_fake_user()
        cls.house = House.objects.create(
            name=fake.address(),
            creator=cls.user,
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.response = self.client.get(
            reverse('house_update', args=(self.house.id,)),
        )

    def test_user_can_edit(self):
        self.assertEqual(self.response.status_code, HttpResponse.status_code)


class UserUpdatesHouse(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = factories.create_fake_user()
        cls.house = House.objects.create(
            name=fake.address(),
            creator=cls.user,
        )
        cls.new_name = fake.address()

    def setUp(self):
        data = {'name': self.new_name}
        self.client.force_login(self.user)
        self.response = self.client.post(
            reverse('house_update', args=(self.house.id,)),
            data=data
        )

    def test_user_is_redirected(self):
        self.assertEqual(self.response.status_code, HttpResponseRedirect.status_code)

    def test_house_is_updated(self):
        house = House.objects.get(id=self.house.id)
        self.assertEqual(house.name, self.new_name)


class UserCreatesRoomate(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = factories.create_fake_user()
        cls.house = House.objects.create(
            name=fake.address(),
            creator=cls.user
        )

    def setUp(self):
        data = {'name': fake.first_name()}
        self.client.force_login(self.user)
        self.response = self.client.post(
            reverse('roommate_create', args=(self.house.id,)),
            data=data,
        )

    def test_user_can_create_roommate(self):
        self.assertEqual(self.response.status_code, HttpResponseRedirect.status_code)

    def test_roommate_is_created(self):
        self.assertEqual(Roommate.objects.count(), 1)

    def test_roommate_is_added_to_house(self):
        self.assertEqual(self.house.roommate_set.count(), 1)
        roommate = Roommate.objects.first()
        self.assertIn(
            roommate.id,
            self.house.roommate_set.values_list('id', flat=True)
        )
