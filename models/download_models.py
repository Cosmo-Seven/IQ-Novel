from django.db import models
from models.base_models import BaseModel
from core.models import NovelModel

class DownloadModel(BaseModel):
    user = models.ForeignKey(
        "core.UserModel",
        on_delete=models.CASCADE,
        related_name="downloads"
    )
    novel = models.ForeignKey(
        NovelModel,
        on_delete=models.CASCADE,
        related_name="downloaded_by"
    )

    class Meta:
        app_label = "core"
        db_table = "downloads"
        verbose_name = "Download"
        verbose_name_plural = "Downloads"
        unique_together = ("user", "novel")

    def __str__(self):
        return f"{self.user.email} downloaded {self.novel.title}"
