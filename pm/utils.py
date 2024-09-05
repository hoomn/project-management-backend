from uuid import uuid4
import os


def attachment_upload_path(instance, filename):
    """
    Generate a unique filename for the uploaded file.
    """
    _, ext = os.path.splitext(filename)
    return os.path.join(instance.content_type.model, instance.content_object.uuid, f"{uuid4()}{ext}")
