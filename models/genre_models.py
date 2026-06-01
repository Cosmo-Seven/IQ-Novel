from django.db import models
from helpers.translation import register_key
from models.base_models import BaseModel
from enums.status import StatusEnum
from django.utils.text import slugify

class GenreModel(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "core"
        db_table = "genres"
        verbose_name = "Genre"
        verbose_name_plural = "Genres"

    def save(self, *args, **kwargs):
        key = slugify(self.name).replace("-", "_").lower()
        register_key(key, self.name)
        super().save(*args, **kwargs)

    @property
    def translation_key(self):
        return slugify(self.name).replace("-", "_").lower()