from django.db import models
from helpers.translation import register_key
from models.base_models import BaseModel
from django.utils.text import slugify


# // Gem Model ------------------------------------------------------
class GemModel(BaseModel):
    gem_amount = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.gem_amount

    class Meta:
        app_label = "core"
        db_table = "gems"
        verbose_name = "Gem"
        verbose_name_plural = "Gems"

    def save(self, *args, **kwargs):
        key = slugify(self.gem_amount).replace("-", "_").lower()
        register_key(key, self.gem_amount)
        super().save(*args, **kwargs)

    @property
    def translation_key(self):
        return slugify(self.gem_amount).replace("-", "_").lower()