from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
from PIL import Image
import os


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='avatars/', null=True, blank=True)
    displayname = models.CharField(max_length=20, null=True, blank=True)
    bio = models.TextField(max_length=150, null=True, blank=True)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)

            width, height = img.size
            min_size = min(width, height)

            left = (width - min_size) // 2
            top = (height - min_size) // 2
            right = (width + min_size) // 2
            bottom = (height + min_size) // 2

            img = img.crop((left, top, right, bottom))
            img = img.resize((300, 300))

            img.save(self.image.path)

    @property
    def name(self):
        if self.displayname:
            name = self.displayname
        else:
            name = self.user.username
        return name
    
    @property
    def avatar(self):
        try:
            avatar = self.image.url
        except:
            avatar = static('images/avatar.svg')
        return avatar
