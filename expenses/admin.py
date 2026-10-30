from django.contrib import admin
from .models import FriendGroup, Currency, Expense

admin.site.register(FriendGroup)
admin.site.register(Currency)
admin.site.register(Expense)