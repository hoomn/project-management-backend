from django.contrib.auth.backends import ModelBackend
from django.utils import timezone
from django.db import transaction

from .models import SingleUseCode


class SingleUseCodeBackend(ModelBackend):
    def authenticate(self, request, code=None, **kwargs):
        if not code:
            return None

        # TODO: Rate Limit Implementation

        try:
            with transaction.atomic():
                single_use_code = SingleUseCode.objects.select_for_update(
                    nowait=True
                ).get(code=code, is_used=False, expires_at__gte=timezone.now())

                # Mark the code as used
                single_use_code.is_used = True
                # single_use_code.used_at = timezone.now()
                single_use_code.save()

                # Update the user's last login
                user = single_use_code.user
                user.last_login = timezone.now()
                user.save(update_fields=["last_login"])

                return user

        except SingleUseCode.DoesNotExist:
            return None
        except transaction.DatabaseError:
            # Handle the case where we couldn't acquire a lock
            return None
