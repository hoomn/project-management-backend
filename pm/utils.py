from django.forms.models import model_to_dict
from django.utils.encoding import force_str
from django.utils.text import Truncator

from datetime import date
from uuid import uuid4
import difflib
import os


def attachment_upload_path(instance, filename):
    """
    Generate a unique filename for the uploaded file.
    """
    _, ext = os.path.splitext(filename)
    return os.path.join(
        instance.content_type.model, instance.content_object.uuid, f"{uuid4()}{ext}"
    )


def get_change_message(instance, data_before_update):
    """
    Compare fields between the instance and the data before update and return a change message of `False`.
    """

    change_message = []
    exclude_list = ["is_archived", "created_by", "updated_by"]

    data_after_update = model_to_dict(instance, exclude=exclude_list)

    for field_name, new_value in data_after_update.items():
        old_value = data_before_update.get(field_name)
        if old_value != new_value:

            # Get verbose field name
            field = instance._meta.get_field(field_name)
            verbose_name = force_str(field.verbose_name)

            # Handle description field
            if field_name == "description":

                change = {
                    "field": field_name,
                    "verbose_name": verbose_name,
                    "old_value": [],
                    "new_value": [],
                }

                # Use difflib for the description field
                diff = list(
                    difflib.unified_diff(old_value.splitlines(), new_value.splitlines())
                )
                if diff:

                    # Skip the metadata
                    for line in diff[2:]:
                        # Skip blank lines (only + or -)
                        if line in ("-", "+"):
                            continue
                        if line.startswith("+"):
                            change["new_value"].append(Truncator(line[1:]).chars(80))
                        elif line.startswith("-"):
                            change["old_value"].append(Truncator(line[1:]).chars(80))

            # If the field is a many-to-many field, convert it to a set of ids to compare
            elif field.many_to_many:

                new = set([u.id for u in new_value])
                old = set([u.id for u in old_value])

                change = {
                    "field": field_name,
                    "verbose_name": verbose_name,
                    "old_value": list(old - new),
                    "new_value": list(new - old),
                    "model": "accounts.user",
                }

            else:

                change = {
                    "field": field_name,
                    "verbose_name": verbose_name,
                    "old_value": old_value,
                    "new_value": new_value,
                }

                # Handle choices fields
                if field.choices:
                    change["old_value"] = dict(field.choices).get(old_value, old_value)
                    change["new_value"] = dict(field.choices).get(new_value, new_value)

                # Handle date fields
                if field.get_internal_type() in ["DateField"]:
                    change["old_value"] = format_date_us(old_value)
                    change["new_value"] = format_date_us(new_value)

            change_message.append(change)

    return change_message or False


def format_date_us(d):
    """
    Convert a datetime.date instance to a US date format with a 3-letter month (e.g., Jul 10, 2024).
    """
    default = "___ __, ____"

    if not d or not isinstance(d, date):
        return default

    try:
        return d.strftime("%b %d, %Y")
    except AttributeError:
        return default
