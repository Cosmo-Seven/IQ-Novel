from django.db import models
from helpers.translation import register_key
from models.base_models import BaseModel
from enums.status import StatusEnum
from django.utils.text import slugify
from core.models import NovelModel

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