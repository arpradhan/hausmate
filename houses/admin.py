from django.contrib import admin

from .models import House, Bill, Roommate, Payment, PaymentEvent

admin.site.register(House)
admin.site.register(Bill)
admin.site.register(Roommate)
admin.site.register(Payment)
admin.site.register(PaymentEvent)
