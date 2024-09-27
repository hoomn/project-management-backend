from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Notification

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notification)
def send_notification_email(sender, instance, created, **kwargs):
    if created:

        # Get the related object (e.g., Activity)
        related_object = instance.content_object

        # TODO: Implement finer control based on the notification category to
        # allow for specific behavior and preferences per category.

        # Check user preferences for email notifications
        # Users should be able to receive single-use code
        if not instance.user.profile.notification and related_object.__class__.__name__ != "SingleUseCode":
            return

        # Check if the related object has a render_notification method
        if hasattr(related_object, "render_notification"):
            message = related_object.render_notification()
        else:
            # Fallback message if the related object doesn't have a render_notification method
            message = {
                "subject": "Notification",
                "body": f"You have a new notification related to {related_object}.",
                "body_html": f"<p>You have a new notification related to {related_object}.</p>",
            }

        subject = message["subject"]
        body = message["body"]
        body_html = message["body_html"]
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.user.email]

        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=body,
                from_email=from_email,
                to=recipient_list,
                alternatives=[(body_html, "text/html")],
            )
            email.send()
        except Exception as e:
            # Log the error
            logger.warning(f"Failed to send email: {e}")
