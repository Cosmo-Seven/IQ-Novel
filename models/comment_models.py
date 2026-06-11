from django.db import models
from models.base_models import BaseModel


class CommentModel(BaseModel):
    novel = models.ForeignKey(
        "core.NovelModel",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        "core.UserModel",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField()
    is_approved = models.BooleanField(default=True)

    class Meta:
        app_label = "core"
        db_table = "comments"
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user} on {self.novel}"
