from django.db import models
import hashlib
import base64


# Create your models here.


def determine_upload_path(instance, filename):
    """Determine upload path for files."""
    return "uploads/{}/{}".format(instance.username, filename)


class Player(models.Model):
    """Player."""

    username = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=40)
    display_name = models.CharField(max_length=7)
    email_address = models.EmailField()
    avatar = models.ImageField(upload_to=determine_upload_path, blank=True)
    sfx = models.FileField(
        "Walkout music", upload_to=determine_upload_path, blank=True
    )

    def __str__(self):
        """Get representation."""
        return self.name

    @property
    def sfx_md5(self):
        """Get sfx hash."""
        hash_md5 = hashlib.md5()
        sfx_data = self.sfx
        try:
            sfx_data.open("rb")
        except ValueError:
            return None
        for chunk in iter(lambda: sfx_data.read(4096), b""):
            hash_md5.update(chunk)
        sfx_data.close()
        return hash_md5.hexdigest()

    @property
    def sfx_data_b64(self):
        """Get SFX data."""
        sfx_data = self.sfx
        try:
            sfx_data.open("rb")
        except ValueError:
            return None

        data_bytes = sfx_data.read()
        sfx_data.close()
        data_b64 = base64.b64encode(data_bytes)
        return data_b64
