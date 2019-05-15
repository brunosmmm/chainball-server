from django.db import models


# Create your models here.


def determine_upload_path(instance, filename):
    """Determine upload path for files."""
    return "uploads/{}/{}".format(instance.username, filename)


class Player(models.Model):
    """Player."""

    name = models.CharField(max_length=40)
    display_name = models.CharField(max_length=7)
    username = models.CharField(max_length=20, unique=True)
    email_address = models.EmailField()
    avatar = models.ImageField(upload_to=determine_upload_path, blank=True)
    sfx = models.FileField(
        "Walkout music", upload_to=determine_upload_path, blank=True
    )

    def __str__(self):
        """Get representation."""
        return self.name
