from django.core.exceptions import ValidationError
import os


# Custom validator for image files
def allow_only_images_validator(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.png', '.jpg', '.jpeg']

    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported file extension. Allowed extensions: " + str(valid_extensions))