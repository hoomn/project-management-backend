from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from notifications.models import EmailLog

from botocore.exceptions import ClientError
import boto3


class SesEmailBackend(BaseEmailBackend):
    """
    Amazon Simple Email Service (SES) backend implementations.
    """

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage instances using Amazon SES
        and return the number of email messages sent successfully.
        """

        log_objects = []
        num_sent = 0

        # Create a new SES resource and specify a region.
        client = boto3.client(
            "ses",
            region_name=settings.AWS_SES_REGION_NAME,
            aws_access_key_id=settings.AWS_SES_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SES_SECRET_KEY,
        )

        for email_message in email_messages:

            body_text = email_message.body
            body_html = None
            for content, content_type in email_message.alternatives:
                if content_type == "text/html":
                    body_html = content

            try:
                response = client.send_email(
                    Destination={"ToAddresses": email_message.to},
                    Message={
                        "Subject": {"Data": email_message.subject, "Charset": "UTF-8"},
                        "Body": {
                            "Text": {"Data": body_text, "Charset": "UTF-8"},
                            "Html": {"Data": body_html, "Charset": "UTF-8"} if body_html else None,
                        },
                    },
                    Source=email_message.from_email,
                )

            except ClientError as e:
                description = f"{ email_message.subject } | { e.response['Error']['Message'] }"
                status = EmailLog.Status.FAIL
            else:
                description = f"{ email_message.subject } | Message ID: { response['MessageId'] }"
                status = EmailLog.Status.SUCCESS
                num_sent += 1

            for recipient in email_message.to:
                log_objects.append(EmailLog(email=recipient, status=status, description=description))

        EmailLog.objects.bulk_create(log_objects)

        return num_sent
