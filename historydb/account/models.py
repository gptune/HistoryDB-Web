from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    affiliation = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    ecp_member = models.CharField(max_length=10, blank=True)
    motivation = models.CharField(max_length=250, blank=True)
    is_certified = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=6, blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
