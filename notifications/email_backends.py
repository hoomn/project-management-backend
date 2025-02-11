from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from notifications.models import EmailLog

from botocore.exceptions import ClientError
import boto3


class SesEmailBackend(BaseEmailBackend):
    """
    Amazon Simple Email Service (SES) backend implementations.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None

    def setup_client(self):
        """
        Initialize the SES client if not already done.
        """
        if self.client is None:
            self.client = boto3.client(
                "ses",
                region_name=settings.AWS_SES_REGION_NAME,
                aws_access_key_id=settings.AWS_SES_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_SES_SECRET_KEY,
            )

    def create_log_entry(self, email, subject, is_success, description):
        """
        Create a standardized log entry for both success and failure cases.
        """
        return EmailLog(
            email=email[:100],
            subject=subject[:100],
            status=EmailLog.Status.SUCCESS if is_success else EmailLog.Status.FAIL,
            description=description,
        )

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage instances using Amazon SES
        and return the number of email messages sent successfully.
        """

        if not email_messages:
            return 0

        self.setup_client()
        log_objects = []
        num_sent = 0

        for email_message in email_messages:

            body_text = email_message.body
            body_html = None

            for content, mime in email_message.alternatives:
                if mime == "text/html":
                    body_html = content
                    break

            try:
                # Prepare the email
                message_data = {
                    "Destination": {"ToAddresses": email_message.to},
                    "Message": {
                        "Subject": {"Data": email_message.subject, "Charset": "UTF-8"},
                        "Body": {
                            "Text": {"Data": body_text, "Charset": "UTF-8"},
                        },
                    },
                    "Source": email_message.from_email,
                }

                # Add HTML content if present
                if body_html:
                    message_data["Message"]["Body"]["Html"] = {"Data": body_html, "Charset": "UTF-8"}

                # Send the email
                response = self.client.send_email(**message_data)
                num_sent += 1

                # Log success for each recipient
                for recipient in email_message.to:
                    log_objects.append(
                        self.create_log_entry(
                            email=recipient,
                            subject=email_message.subject,
                            is_success=True,
                            description=f"Message ID: { response['MessageId'] }",
                        )
                    )

            except ClientError as e:
                error_message = e.response["Error"]["Message"]
                # Log AWS-specific errors for each recipient
                for recipient in email_message.to:
                    log_objects.append(
                        self.create_log_entry(
                            email=recipient,
                            subject=email_message.subject,
                            is_success=False,
                            description=f"Client Error: {error_message}",
                        )
                    )

            except Exception as e:
                # Log unexpected errors for each recipient
                for recipient in email_message.to:
                    log_objects.append(
                        self.create_log_entry(
                            email=recipient,
                            subject=email_message.subject,
                            is_success=False,
                            description=f"Unexpected Error: {str(e)}",
                        )
                    )

        EmailLog.objects.bulk_create(log_objects)

        return num_sent
