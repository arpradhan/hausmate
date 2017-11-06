from faker import Faker

from django.test import TestCase
from django.urls import reverse
from django.http.response import HttpResponseRedirect, HttpResponse

from core import factories

from houses.models import House, Roommate, Bill

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

    def test_roommate_is_created(self):
        house = House.objects.first()
        roommates = house.roommate_set
        self.assertEqual(roommates.count(), 1)
        self.assertIn(self.user.first_name, roommates.values_list('name', flat=True))


class HouseDataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.user = factories.create_fake_user()
        cls.house = House.objects.create(
            name=fake.address(),
            creator=cls.user
        )


class UserVisitsHouseList(HouseDataMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
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


class AnonUserVisitsHouse(HouseDataMixin, TestCase):
    def setUp(self):
        self.response = self.client.get(
            reverse('house_detail', args=(self.house.id,))
        )

    def test_user_is_redirected(self):
        self.assertEqual(self.response.status_code, HttpResponseRedirect.status_code)


class UserVisitsHouse(HouseDataMixin, TestCase):
    def setUp(self):
        self.client.force_login(self.user)
        self.response = self.client.get(
            reverse('house_detail', args=(self.house.id,))
        )

    def test_user_can_view_house(self):
        self.assertEqual(self.response.status_code, HttpResponse.status_code)


class AnonUserDeletesHouse(HouseDataMixin, TestCase):
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


class TestAnonUserUpdatesHouse(HouseDataMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.name = fake.address()
        cls.house.name = cls.name
        cls.house.save()

    def setUp(self):
        data = {'name': fake.address()}
        self.response = self.client.post(
            reverse('house_update', args=(self.house.id,)),
            data=data,
        )

    def test_house_is_not_update(self):
        house = House.objects.get(id=self.house.id)
        self.assertEqual(house.name, self.name)

    def test_user_is_redirected(self):
        self.assertEqual(self.response.status_code, HttpResponseRedirect.status_code)


class UserVisitsUpdateHouse(HouseDataMixin, TestCase):
    def setUp(self):
        self.client.force_login(self.user)
        self.response = self.client.get(
            reverse('house_update', args=(self.house.id,)),
        )

    def test_user_can_edit(self):
        self.assertEqual(self.response.status_code, HttpResponse.status_code)


class UserUpdatesHouse(HouseDataMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
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


class UserVisitsCreateRoommate(HouseDataMixin, TestCase):
    def setUp(self):
        self.client.force_login(self.user)
        self.response = self.client.get(
            reverse('roommate_create', args=(self.house.id,)),
        )

    def test_user_can_view(self):
        self.assertEqual(self.response.status_code, HttpResponse.status_code)


class UserCreatesRoomate(HouseDataMixin, TestCase):
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


class UserVisitsCreateBill(HouseDataMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.r1 = Roommate.objects.create(name=fake.first_name(), house=cls.house)
        cls.r2 = Roommate.objects.create(name=fake.first_name(), house=cls.house)

    def setUp(self):
        self.client.force_login(self.user)
        self.response = self.client.get(
            reverse('bill_create', args=(self.house.id,))
        )

    def test_user_can_view(self):
        self.assertEqual(self.response.status_code, HttpResponse.status_code)

    def test_roommates_in_owner_select(self):
        roommates = self.response.context['roommates']
        roommate_ids = [r['id'] for r in roommates]
        self.assertIn(self.r1.id, roommate_ids)
        self.assertIn(self.r2.id, roommate_ids)


class UserCreatesBill(HouseDataMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.roommate = Roommate.objects.create(name=fake.first_name(), house=cls.house)

    def setUp(self):
        data = {'name': 'Internet', 'amount': 80.00, 'owner': self.roommate.id}
        self.client.force_login(self.user)
        self.response = self.client.post(
            reverse('bill_create', args=(self.house.id,)),
            data=data,
        )

    def test_bill_is_created(self):
        self.assertEqual(self.response.status_code, HttpResponseRedirect.status_code)
        self.assertEqual(Bill.objects.count(), 1)

    def test_bill_belongs_to_roommate(self):
        bill = Bill.objects.first()
        self.assertEqual(bill.owner.id, self.roommate.id)
