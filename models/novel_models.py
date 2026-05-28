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

# class ReadingHistory(BaseModel):
#     user = models.ForeignKey("core.UserModel", on_delete=models.CASCADE)
#     novel = models.ForeignKey(NovelModel, on_delete=models.CASCADE)
#     last_chapter = models.ForeignKey(
#         ChapterModel,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True
#     )

#     def __str__(self):
#         return f"{self.user} reading {self.novel}"


# ---------- Chapter Purchase ---------- #

# class ChapterPurchase(BaseModel):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     chapter = models.ForeignKey(ChapterModel, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.user} bought {self.chapter}"

#     class Meta:
#         unique_together = ('user', 'chapter')
    