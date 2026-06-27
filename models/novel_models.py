from django.db import models
from helpers.translation import register_key
from models.base_models import BaseModel
from enums.status import StatusEnum
from django.utils.text import slugify
from core.models import GenreModel

# ---------- Novel ---------- #
class NovelModel(BaseModel):
    class NovelType(models.TextChoices):
        FANFIC = 'fanfic', 'Fanfic'
        TRANSLATE = 'translate', 'Translate'
        OWN_CREATION = 'own_creation', 'Own Creation'

    title = models.CharField(max_length=255)

    cover_image = models.ImageField(upload_to='novels/')
    summary = models.TextField()

    novel_type = models.CharField(
        max_length=20,
        choices=NovelType.choices,
        default=NovelType.OWN_CREATION,
        null=True,
        blank=True,
    )

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