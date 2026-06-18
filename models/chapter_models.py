from django.db import models
from helpers.translation import register_key
from models.base_models import BaseModel
from enums.status import StatusEnum
from django.utils.text import slugify
from core.models import NovelModel
from ckeditor.fields import RichTextField

class ChapterModel(BaseModel):
    novel = models.ForeignKey(
        NovelModel,
        on_delete=models.CASCADE,
        related_name="chapters"
    )

    chapter_title = models.CharField(max_length=255)

    content = RichTextField(config_name='default')
    is_free = models.BooleanField(default=False)

    gem_price = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.novel.title} - Chapter {self.chapter_title}"
    
    class Meta:
        app_label = "core"
        db_table = "chapters"
        verbose_name = "Chapter"
        verbose_name_plural = "Chapters"
        ordering = ['chapter_title']
        unique_together = ('novel', 'chapter_title')

    def save(self, *args, **kwargs):
        key = slugify(self.chapter_title).replace("-", "_").lower()
        register_key(key, self.chapter_title)
        super().save(*args, **kwargs)

    @property
    def translation_key(self):
        return slugify(self.title).replace("-", "_").lower()

# ---------- Chapter Purchase ---------- #
class ChapterPurchaseModel(BaseModel):
    user = models.ForeignKey(
        "core.UserModel",
        on_delete=models.CASCADE,
        related_name="chapter_purchases",
    )
    chapter = models.ForeignKey(
        ChapterModel,
        on_delete=models.CASCADE,
        related_name="purchased_by",
    )
    gems_paid = models.PositiveIntegerField(default=0)
    sale_price_mmk = models.PositiveIntegerField(default=0)
    author_share_mmk = models.PositiveIntegerField(default=0)
    gem_unit_price_mmk = models.PositiveIntegerField(
        default=0,
        help_text="MMK per gem at time of purchase (for historical records).",
    )
    revenue_share_percent = models.PositiveSmallIntegerField(default=0)

    class Meta:
        app_label = "core"
        db_table = "chapter_purchases"
        verbose_name = "Chapter Purchase"
        verbose_name_plural = "Chapter Purchases"
        unique_together = ("user", "chapter")

    def __str__(self):
        return f"{self.user.email} bought {self.chapter}"


# ---------- Chapter Read Progress ---------- #
class ChapterReadModel(BaseModel):
    user = models.ForeignKey(
        "core.UserModel",
        on_delete=models.CASCADE,
        related_name="chapter_reads",
    )
    chapter = models.ForeignKey(
        ChapterModel,
        on_delete=models.CASCADE,
        related_name="read_by",
    )

    class Meta:
        app_label = "core"
        db_table = "chapter_reads"
        verbose_name = "Chapter Read"
        verbose_name_plural = "Chapter Reads"
        unique_together = ("user", "chapter")

    def __str__(self):
        return f"{self.user.email} read {self.chapter}"