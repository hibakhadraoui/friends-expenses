from django.db import models
from django.contrib.auth.models import User


class FriendGroup(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name="friend_groups")

    def __str__(self):
        return self.name


class Currency(models.Model):
    group = models.ForeignKey(FriendGroup, on_delete=models.CASCADE)
    code = models.CharField(max_length=5)  # for example USD
    rate_to_eur = models.DecimalField(max_digits=10, decimal_places=4)  # 1 unit = how many euros

    def __str__(self):
        return self.code + " (" + self.group.name + ")"


class Expense(models.Model):
    group = models.ForeignKey(FriendGroup, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, blank=True)  # empty means euros
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="paid_expenses")
    beneficiaries = models.ManyToManyField(User, related_name="benefited_expenses")

    def __str__(self):
        return self.description