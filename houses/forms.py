from django import forms
from .models import PaymentEvent, Payment


class PaymentEventForm(forms.ModelForm):
    class Meta:
        model = PaymentEvent
        fields = ['amount', 'payment']

    def clean_amount(self):
        data = self.cleaned_data['amount']
        payment = Payment.objects.get(id=self.data['payment'])
        if data > payment.amount:
            raise forms.ValidationError('Amount is greater than total payment.')
        return data
