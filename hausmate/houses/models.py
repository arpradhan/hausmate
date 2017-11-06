from decimal import Decimal

from django.db import models
from django.conf import settings


class House(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True)

    def __str__(self):
        return self.name


class Roommate(models.Model):
    name = models.CharField(max_length=200)
    house = models.ForeignKey(House, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Bill(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    owner = models.ForeignKey(Roommate, on_delete=models.CASCADE)
    house = models.ForeignKey(House, on_delete=models.CASCADE, null=True)
    due_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

    @property
    def amount_due(self):
        payments = self.payment_set.all()
        amount_paid_sum = payments.aggregate(
            models.Sum('amount_paid'))['amount_paid__sum']
        return Decimal(self.amount) - amount_paid_sum

    @property
    def amount_paid(self):
        payments = self.payment_set.all()
        return payments.aggregate(
            models.Sum('amount_paid'))['amount_paid__sum']

    def create_split_payments(self):
        roommate_count = self.house.roommate_set.count()
        split_amount = self.amount / roommate_count
        for roommate in self.house.roommate_set.all():
            Payment.objects.create(
                bill=self,
                payer=roommate,
                amount=split_amount,
            )


class Payment(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    payer = models.ForeignKey(Roommate, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return '{}'.format(self.amount)

    @property
    def is_paid(self):
        return self.amount == self.amount_paid

    @property
    def amount_due(self):
        return self.amount - self.amount_paid


class PaymentEvent(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        payment = self.payment
        payment.amount_paid += Decimal(self.amount)
        payment.save()
