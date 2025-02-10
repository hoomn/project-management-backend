from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from notifications.models import Notification


class Command(BaseCommand):
    help = "Cleans up notifications with invalid generic relations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force deletion without confirmation",
        )

    def handle(self, *args, **options):
        # Get total count of notifications
        total_notifications = Notification.objects.count()

        # Get all valid content types
        valid_content_types = ContentType.objects.values_list("id", flat=True)

        # Find notifications with invalid content types
        invalid_ct_notifications = Notification.objects.exclude(content_type_id__in=valid_content_types)
        invalid_ct_count = invalid_ct_notifications.count()

        # Find notifications with missing objects
        remaining = Notification.objects.filter(content_type_id__in=valid_content_types)
        invalid_obj_notifications = []

        for notification in remaining:
            try:
                if notification.content_object is None:
                    invalid_obj_notifications.append(notification.id)
            except (ObjectDoesNotExist, AttributeError):
                invalid_obj_notifications.append(notification.id)

        invalid_obj_count = len(invalid_obj_notifications)
        total_invalid = invalid_ct_count + invalid_obj_count

        if total_invalid == 0:
            self.stdout.write(self.style.SUCCESS("No invalid notifications found."))
            return

        # Show summary and ask for confirmation
        self.stdout.write(
            f"\nFound {total_invalid} invalid notifications out of {total_notifications} total:"
            f"\n - {invalid_ct_count} notifications with invalid content types"
            f"\n - {invalid_obj_count} notifications with missing objects"
        )

        if not options["force"]:
            confirm = input("\nDo you want to proceed with deletion? [y/N]: ")
            if confirm.lower() != "y":
                self.stdout.write(self.style.WARNING("Operation cancelled."))
                return

        # Perform deletion
        deleted_ct = invalid_ct_notifications.delete()[0]
        deleted_obj = Notification.objects.filter(id__in=invalid_obj_notifications).delete()[0]

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully cleaned up:"
                f"\n - {deleted_ct} notifications with invalid content types"
                f"\n - {deleted_obj} notifications with missing objects"
            )
        )
