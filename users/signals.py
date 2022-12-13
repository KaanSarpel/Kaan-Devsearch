from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import Profile

from django.core.mail import send_mail
from django.conf import settings #signals.py'dan sonra Django'ya tanıt apps.py'da yapabilirsin bunu.

# @receiver(post_save, sender=Profile)


def createProfile(sender, instance, created, **kwargs): #Anytime we add a user a profile is autamatically created. Sender the Model that sends it.Instance of a model that actually triggered this or object.Created true or false.
    if created:
        user = instance
        profile = Profile.objects.create(
            user=user,
            username=user.username,
            email=user.email,
            name=user.first_name,
        )

        subject = 'Welcome to DevSearch'
        message = 'We are glad you are here!'

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [profile.email],
            fail_silently=False,
        )


def updateUser(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user

    if created == False:
        user.first_name = profile.name
        user.username = profile.username
        user.email = profile.email
        user.save()


def deleteUser(sender, instance, **kwargs): #Instance here is the Profile.
    try:
        user = instance.user
        user.delete()
    except:
        pass


post_save.connect(createProfile, sender=User) #Everytime save method is called on a User(User gets created) model trigger this method.
post_save.connect(updateUser, sender=Profile) #This time we will trigger UpdateUser / anytime the Profile is updated we will trigger updateUser method.
post_delete.connect(deleteUser, sender=Profile) #Anytime Profile is deleted trigger deleteUser function.
