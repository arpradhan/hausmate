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
