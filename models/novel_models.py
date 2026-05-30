from django.db import models
from helpers.translation import register_key
from models.base_models import BaseModel
from enums.status import StatusEnum
from django.utils.text import slugify


# ---------- Genre ---------- #

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
    

# ---------- Novel ---------- #

class NovelModel(BaseModel):
    title = models.CharField(max_length=255)

    cover_image = models.ImageField(upload_to='novels/')
    summery = models.TextField()

    genres = models.ManyToManyField(GenreModel, related_name="novels")
    status = models.CharField(max_length=10, choices=StatusEnum.choices, default=StatusEnum.ONGOING)

    views = models.PositiveIntegerField(default=0)

    is_completed = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    is_fanfic = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)

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
    

# ---------- Chapter ---------- #

class NovelChapterModel(BaseModel):
    novel = models.ForeignKey(
        NovelModel,
        on_delete=models.CASCADE,
        related_name="chapters"
    )

    chapter_title = models.CharField(max_length=255)

    content = models.TextField()

    is_free = models.BooleanField(default=True)
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


# ---------- Reading History ---------- #

class BookmarkModel(BaseModel):
    user = models.ForeignKey(
        "core.UserModel",
        on_delete=models.CASCADE,
        related_name="bookmarks"
    )
    novel = models.ForeignKey(
        NovelModel,
        on_delete=models.CASCADE,
        related_name="bookmarked_by"
    )

    class Meta:
        app_label = "core"
        db_table = "bookmarks"
        verbose_name = "Bookmark"
        verbose_name_plural = "Bookmarks"
        unique_together = ("user", "novel")

    def __str__(self):
        return f"{self.user.email} bookmarked {self.novel.title}"


# ---------- Chapter Purchase ---------- #
class ChapterPurchaseModel(BaseModel):
    user = models.ForeignKey(
        "core.UserModel",
        on_delete=models.CASCADE,
        related_name="chapter_purchases",
    )
    chapter = models.ForeignKey(
        NovelChapterModel,
        on_delete=models.CASCADE,
        related_name="purchased_by",
    )

    class Meta:
        app_label = "core"
        db_table = "chapter_purchases"
        verbose_name = "Chapter Purchase"
        verbose_name_plural = "Chapter Purchases"
        unique_together = ("user", "chapter")

    def __str__(self):
        return f"{self.user.email} bought {self.chapter}"
    