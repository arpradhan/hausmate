from decimal import Decimal
from faker import Faker

from django.test import TestCase

from core import factories
from houses.models import House, Roommate, Bill, Payment, PaymentEvent

fake = Faker()


class BillDataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.user = factories.create_fake_user()
        cls.house = House.objects.create(
            creator=cls.user,
            name=fake.address(),
        )
        for i in range(4):
            Roommate.objects.create(
                name=fake.first_name(),
                house=cls.house,
            )
        cls.bill = Bill.objects.create(
            name='Electric',
            amount=64.00,
            owner=Roommate.objects.first(),
            house=cls.house,
        )


class CreateSplitPaymentsTest(BillDataMixin, TestCase):
    def setUp(self):
        self.bill.create_split_payments()

    def test_payments_are_created(self):
        self.assertEqual(Payment.objects.count(), 4)

    def test_payments_are_split_equally(self):
        payments = Payment.objects.filter(bill=self.bill)
        for payment in payments:
            self.assertEqual(payment.amount, 16.00)


class BillAmountDueTest(BillDataMixin, TestCase):
    def setUp(self):
        self.bill.create_split_payments()
        payment = self.bill.payment_set.first()
        payment.amount_paid = 16.00
        payment.save()

    def test_payment_is_deducted_from_amount_due(self):
        amount_due = self.bill.amount_due
        self.assertEqual(amount_due, 48.00)


class BillAmountPaidTest(BillDataMixin, TestCase):
    def setUp(self):
        self.bill.create_split_payments()
        payments = self.bill.payment_set.all()
        for payment in payments:
            payment.amount_paid = 8.00
            payment.save()

    def test_payments_are_added_to_amount_paid(self):
        amount_paid = self.bill.amount_paid
        self.assertEqual(amount_paid, 32.00)


class CreatePaymentEvent(BillDataMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.bill.create_split_payments()
        cls.payment = Payment.objects.first()
        cls.payment_amount = cls.payment.amount
        cls.payment_event_amount = 8.00

    def setUp(self):
        PaymentEvent.objects.create(
            payment=self.payment,
            amount=self.payment_event_amount,
        )

    def test_payment_amount_paid_is_increased(self):
        self.assertEqual(
            self.payment.amount_paid,
            Decimal(self.payment_amount) - Decimal(self.payment_event_amount),
        )


class RoommatePaymentHistory(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = factories.create_fake_user()
        house = House.objects.create(
            creator=cls.user,
            name=fake.address(),
        )
        cls.roommate = Roommate.objects.create(name=fake.first_name(), house=house)
        r2 = Roommate.objects.create(name=fake.first_name(), house=house)
        r3 = Roommate.objects.create(name=fake.first_name(), house=house)
        cls.b1 = Bill.objects.create(
            name='Internet',
            amount=100.00,
            owner=r2,
            house=house,
        )
        cls.b2 = Bill.objects.create(
            name='Heat',
            amount=50.00,
            owner=r3,
            house=house,
        )
        cls.p1 = Payment.objects.create(
            bill=cls.b1,
            amount=50.00,
            payer=cls.roommate,
        )
        cls.p2 = Payment.objects.create(
            bill=cls.b2,
            amount=25.00,
            payer=cls.roommate,
        )

    def setUp(self):
        self.pe1 = PaymentEvent.objects.create(
            amount=10.00,
            payment=self.p1,
        )
        self.pe2 = PaymentEvent.objects.create(
            amount=20.00,
            payment=self.p2,
        )
        self.pe3 = PaymentEvent.objects.create(
            amount=30.00,
            payment=self.p1,
        )
        self.payment_history = self.roommate.payment_history()

    def test_payment_history_ordering(self):
        history = self.payment_history
        self.assertEqual(history[0].id, self.pe3.id)
        self.assertEqual(history[1].id, self.pe2.id)
        self.assertEqual(history[2].id, self.pe1.id)


class AmountsOwedFromRoommates(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = factories.create_fake_user()
        house = House.objects.create(
            creator=cls.user,
            name=fake.address(),
        )
        cls.roommate = Roommate.objects.create(name=fake.first_name(), house=house)
        cls.r2 = Roommate.objects.create(name=fake.first_name(), house=house)
        r3 = Roommate.objects.create(name=fake.first_name(), house=house)
        b1 = Bill.objects.create(
            name='Internet',
            amount=100.00,
            owner=cls.roommate,
            house=house,
        )
        b2 = Bill.objects.create(
            name='Heat',
            amount=100.00,
            owner=cls.roommate,
            house=house,
        )
        b3 = Bill.objects.create(
            name='Electric',
            amount=100.00,
            owner=cls.roommate,
            house=house,
        )
        for bill in [b1, b2, b3]:
            Payment.objects.create(
                bill=bill,
                amount=25.00,
                payer=r3,
            )
            Payment.objects.create(
                bill=bill,
                amount=50.00,
                payer=cls.r2,
            )

    def setUp(self):
        self.amounts_owed_from_roommates = self.roommate.amounts_owed_from_roommates()

    def test_amounts(self):
        self.assertEqual(
            self.amounts_owed_from_roommates[0]['amount'],
            150.00,
        )


class AmountsOwedToRoommates(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = factories.create_fake_user()
        house = House.objects.create(
            creator=cls.user,
            name=fake.address(),
        )
        cls.roommate = Roommate.objects.create(name=fake.first_name(), house=house)
        r2 = Roommate.objects.create(name=fake.first_name(), house=house)
        b1 = Bill.objects.create(
            name='Internet',
            amount=100.00,
            owner=r2,
            house=house,
        )
        b2 = Bill.objects.create(
            name='Heat',
            amount=100.00,
            owner=r2,
            house=house,
        )
        b3 = Bill.objects.create(
            name='Electric',
            amount=100.00,
            owner=r2,
            house=house,
        )
        for bill in [b1, b2, b3]:
            Payment.objects.create(
                bill=bill,
                amount=50.00,
                payer=cls.roommate,
            )

    def setUp(self):
        self.amounts_owed_to_roommates = self.roommate.amounts_owed_to_roommates()

    def test_amounts(self):
        self.assertEqual(
            self.amounts_owed_to_roommates[0]['amount'],
            150.00,
        )
