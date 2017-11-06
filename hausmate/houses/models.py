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

    def __str__(self):
        return self.name


class Payment(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    payer = models.ForeignKey(Roommate, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        '{} owed for {}'.format(self.amount, self.bill.name)

    @property
    def is_paid(self):
        return self.amount == self.amount_paid

    @property
    def amount_due(self):
        return self.amount - self.amount_paid
