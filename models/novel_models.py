from django.db import models
from helpers.translation import register_key
from models.base_models import BaseModel
from enums.status import StatusEnum
from django.utils.text import slugify
from core.models import GenreModel

# ---------- Novel ---------- #
class NovelModel(BaseModel):
    title = models.CharField(max_length=255)

    cover_image = models.ImageField(upload_to='novels/')
    summery = models.TextField()

    genres = models.ManyToManyField(GenreModel, related_name="novels")
    status = models.CharField(max_length=10, choices=StatusEnum.choices, default=StatusEnum.ONGOING)

    author = models.ForeignKey(
        "core.AuthorModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="novels",
    )

    views = models.PositiveIntegerField(default=0)

    is_completed = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    is_fanfic = models.BooleanField(default=False)
    

    def __str__(self):
        return self.title

    class Meta:
        app_label = "core"
        db_table = "novels"
        verbose_name = "Novel"
        verbose_name_plural = "Novels"

    def save(self, *args, **kwargs):
        key = slugify(self.title).replace("-", "_").lower()
        register_key(key, self.title)
        super().save(*args, **kwargs)

    @property
    def translation_key(self):
        return slugify(self.title).replace("-", "_").lower()