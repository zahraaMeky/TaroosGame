import datetime
from ipaddress import ip_address
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import models
from django.utils import timezone



# Model to store the list of logged in users
#track user login 
class extend_user(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_login = models.IntegerField(default=0)
    phone = models.CharField(max_length=8)
    IP = models.CharField(max_length=20, default=None,null=True)

class GamePlans(models.Model):
    PlanName = models.CharField(max_length=50)
    PlanAccounts = models.IntegerField()
    PlanPrice = models.IntegerField()
    def Annual_Price(self):
        return self.PlanPrice * 12


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(GamePlans, on_delete=models.CASCADE)
    subscribeperiod = models.CharField(max_length=20)
    active = models.BooleanField(default=False)
    createdDate = models.DateField()
    expiredDate  = models.DateField()
    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         self.expiredDate = self.createdDate + datetime.timedelta(days=30)
    #     super(UserSubscription, self).save(*args, **kwargs)


