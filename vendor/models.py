from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import sendNotification


# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='user_profile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=100)
    vendor_license = models.ImageField(upload_to='vendors/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.vendor_name
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            # update
            orig = Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                mailTemplate = "accounts/emails/adminApprovalEmail.html",
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                }

                if self.is_approved == True:
                    mailSubject = "Congratulations!, Your restaurant has been approved."
                else:
                    mailSubject = "We are sorry! You are not eligible for publishing your food menu on our marketplace."
                # Send notification email based on approval status
                sendNotification(mailSubject, mailTemplate, context)
        return super(Vendor, self).save(*args, **kwargs)
