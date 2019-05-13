from django.db import models

# Create your models here.
class Player(models.Model):
    """Player."""

    name = models.CharField(max_length=40)
    display_name = models.CharField(max_length=7)
    email_address = models.EmailField()
    avatar = models.ImageField(blank=True)

    def __str__(self):
        """Get representation."""
        return self.name
