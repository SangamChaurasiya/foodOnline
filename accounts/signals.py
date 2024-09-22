from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from accounts.models import User, UserProfile


@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        # Creating User Profile when new user created
        UserProfile.objects.create(user=instance) # Creating the User Profile when user is created
    else:
        try:
            # Updating the User Profile if Profile exists for already created users
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # Creating User Profile if profile does not exist for already created users
            UserProfile.objects.create(user=instance)

# post_save.connect(post_save_create_profile_receiver, sender=User)


@receiver(pre_save, sender=User)
def pre_save_profile_receiver(sender, instance, **kwargs):
    print(instance.username, ' is being started for saving.')
