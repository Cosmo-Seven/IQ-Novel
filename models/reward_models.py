from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from models.base_models import BaseModel


# ---------- Reward ---------- #
class RewardModel(BaseModel):
    class RewardType(models.TextChoices):
        GEM_GIFT      = "gem_gift",      "Gem Gift (Login Reward)"
        FREE_READ     = "free_read",     "Free Read (All Chapters Free)"
        DISCOUNT_READ = "discount_read", "Discount Read (All Chapters 1 Gem)"
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount     = models.PositiveIntegerField(default=0, help_text="gem_gift အတွက်သာ သုံး၊ free_read/discount_read မှာ 0 ထားပါ")
    reward_type = models.CharField(max_length=20,choices=RewardType.choices,default=RewardType.GEM_GIFT,)
    user = models.ForeignKey("core.UserModel",on_delete=models.CASCADE,blank=True,null=True,related_name="rewards",help_text="None ဆိုရင် user အားလုံးအတွက်")

    class Meta:
        app_label = "core"
        db_table = "reward"
        verbose_name = "Reward"
        verbose_name_plural = "Reward"
    
    def is_active_now(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date


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
