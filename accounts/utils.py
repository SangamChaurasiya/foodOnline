from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings


def detectUser(user):
    if user.role == 1:
        return "vendor:vendorDashboard"
    elif user.role == 2:
        return "accounts:customerDashboard"
    elif user.role == None and user.is_superadmin:
        return "/admin"
    

def send_verification_email(request, user, mailSubject, emailTemplate):
    from_email = settings.DEFAULT_FROM_EMAIL
    currentSite = get_current_site(request)
    
    message = render_to_string(emailTemplate, {
        'user': user,
        'domain': currentSite,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user)
    })
    toEmail = user.email
    mail = EmailMessage(mailSubject, message, from_email=from_email, to=[toEmail])
    mail.content_subtype = "html"
    mail.send()


def sendNotification(mailSubject, mailTemplate, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(mailTemplate, context)
    if isinstance(context['to_email'], str):
        toEmail = []
        toEmail.append(context["to_email"])
    else:
        toEmail = context["to_email"]
    mail = EmailMessage(mailSubject, message, from_email=from_email, to=toEmail)
    mail.content_subtype = "html"
    mail.send()

