from django.contrib import admin

from .models import House, Bill, Roommate

admin.site.register(House)
admin.site.register(Bill)
admin.site.register(Roommate)
