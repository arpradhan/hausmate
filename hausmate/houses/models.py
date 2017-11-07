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

    def payment_history(self):
        payments = self.payment_set
        payment_events = PaymentEvent.objects.filter(
            payment__in=payments.values_list('id', flat=True)
        ).order_by('-created')
        return payment_events

    def amounts_owed_from_roommates(self):
        # List of total amounts owed by each roommate to the current roomamte
        roommates = self.house.roommate_set.exclude(id=self.id)
        amounts = []
        for roommate in roommates:
            data = {}
            payments = roommate.payment_set.filter(
                bill__owner_id=self.id,
            )
            if payments.count() > 0:
                amount_paid_sum = payments.aggregate(
                    models.Sum('amount_paid'))['amount_paid__sum']
                amount_sum = payments.aggregate(
                    models.Sum('amount'))['amount__sum']
                data['amount'] = amount_sum - amount_paid_sum
                data['roommate_name'] = roommate.name
                amounts.append(data)
        return amounts

    def amounts_owed_to_roommates(self):
        roommates = self.house.roommate_set.exclude(id=self.id)
        amounts = []
        for roommate in roommates:
            data = {}
            payments = self.payment_set.filter(
                bill__owner_id=roommate.id
            )
            if payments.count() > 0:
                amount_paid_sum = payments.aggregate(
                    models.Sum('amount_paid'))['amount_paid__sum']
                amount_sum = payments.aggregate(
                    models.Sum('amount'))['amount__sum']
                data['amount'] = amount_sum - amount_paid_sum
                data['roommate_name'] = roommate.name
                if data['amount'] > 0.00:
                    amounts.append(data)
        return amounts


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
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return '{payer} paid {amount} to {payee} for {bill}'.format(
            payer=self.payment.payer.name,
            amount=self.amount,
            payee=self.payment.bill.owner.name,
            bill=self.payment.bill.name,
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        payment = self.payment
        payment.amount_paid = Decimal(payment.amount_paid) + Decimal(self.amount)
        payment.save()
