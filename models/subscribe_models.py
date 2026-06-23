# core/models/novel_subscription.py

from django.db import models
from models.base_models import BaseModel


class NovelPushSubscriptionModel(BaseModel):
    user = models.ForeignKey(
        "core.UserModel",
        on_delete=models.CASCADE,
        related_name="novel_push_subscriptions",
    )
    novel = models.ForeignKey(
        "core.NovelModel",
        on_delete=models.CASCADE,
        related_name="push_subscribers",
    )

    endpoint   = models.TextField(unique=True)
    p256dh_key = models.TextField()
    auth_key   = models.TextField()

    class Meta:
        app_label  = "core"
        db_table   = "novel_push_subscriptions"
        unique_together = ("user", "novel", "endpoint")
        verbose_name = "Novel Push Subscription"

    def __str__(self):
        return f"{self.user.email} → {self.novel.title}"