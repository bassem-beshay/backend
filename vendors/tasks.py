from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import logging

from .models import Vendor

logger = logging.getLogger(__name__)

def send_vendor_email(vendor_id, template_name, subject, context):
    try:
        vendor = Vendor.objects.get(id=vendor_id)
        context['vendor'] = vendor
        context['site_name'] = settings.SITE_NAME

        message = render_to_string(template_name, context)
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[vendor.contact_email],
            html_message=message,
            fail_silently=False,
        )
        
        logger.info(f"send {subject} mail to {vendor.contact_email}")

    except ObjectDoesNotExist:
        logger.error(f"Vendor with ID {vendor_id} does not exist.")
    except Exception as e:
        logger.exception(f"Failed to send email to vendor ID {vendor_id}: {str(e)}")


def send_vendor_approval_email(vendor_id):
    send_vendor_email(
        vendor_id=vendor_id,
        template_name='vendors/emails/approval_email.html',
        subject='Your Vendor Account Has Been Approved',
        context={}
    )


def send_vendor_rejection_email(vendor_id, reason=""):
    send_vendor_email(
        vendor_id=vendor_id,
        template_name='vendors/emails/rejection_email.html',
        subject='Your Vendor Application Status',
        context={'reason': reason}
    )
