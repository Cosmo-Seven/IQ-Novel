from django.db import models
from models.base_models import BaseModel


class NovelViewModel(BaseModel):
    novel = models.ForeignKey(
        "core.NovelModel",
        on_delete=models.CASCADE,
        related_name="novel_views",
    )
    user = models.ForeignKey(
        "core.UserModel",
        on_delete=models.CASCADE,
        related_name="novel_views",
    )

    class Meta:
        app_label = "core"
        db_table = "novel_views"
        verbose_name = "Novel View"
        verbose_name_plural = "Novel Views"
        unique_together = (("novel", "user"),)

    def __str__(self):
        return f"{self.user} viewed {self.novel}"
