from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from models.base_models import BaseModel


# ---------- Reward ---------- #
class RewardModel(BaseModel):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount = models.PositiveIntegerField()
    user = models.ForeignKey(
        "core.UserModel",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="rewards",
    )

    class Meta:
        app_label = "core"
        db_table = "reward"
        verbose_name = "Reward"
        verbose_name_plural = "Reward"


# ---------- Daily Reward Claim ---------- #
class DailyRewardModel(BaseModel):
    reward = models.ForeignKey(RewardModel, on_delete=models.CASCADE, related_name="daily_claims")
    user = models.ForeignKey("core.UserModel", on_delete=models.CASCADE, related_name="daily_reward_claims")
    claim_date = models.DateField(auto_now_add=True)
    amount_received = models.PositiveIntegerField()

    class Meta:
        app_label = "core"
        db_table = "daily_reward_claim"
        verbose_name = "Daily Reward Claim"
        verbose_name_plural = "Daily Reward Claims"
        unique_together = ("reward", "user", "claim_date")
