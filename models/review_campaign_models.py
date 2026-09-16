from django.db import models
from django.utils import timezone
from models.base_models import BaseModel


# ---------- Review Campaign (Admin sets the contest period) ---------- #
class ReviewCampaignModel(BaseModel):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, default="")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    reward_amount = models.PositiveIntegerField(
        default=0,
        help_text="Winner တစ်ယောက်စီကို ပေးမယ့် diamond (gem) အရေအတွက်",
    )

    class Meta:
        app_label = "core"
        db_table = "review_campaigns"
        verbose_name = "Review Campaign"
        verbose_name_plural = "Review Campaigns"

    def __str__(self):
        return self.title

    def is_active_now(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def has_ended(self):
        return timezone.now() > self.end_date

    @property
    def winner_reviews(self):
        return self.reviews.filter(is_deleted=False, is_winner=True)

    @property
    def winner_count(self):
        return self.winner_reviews.count()


# ---------- Campaign Review (Reader submission: novel + image + text) ---------- #
class CampaignReviewModel(BaseModel):
    campaign = models.ForeignKey(
        ReviewCampaignModel,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    novel = models.ForeignKey(
        "core.NovelModel",
        on_delete=models.CASCADE,
        related_name="campaign_reviews",
    )
    user = models.ForeignKey(
        "core.UserModel",
        on_delete=models.CASCADE,
        related_name="campaign_reviews",
    )
    image = models.ImageField(upload_to="campaign_reviews")
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    is_winner = models.BooleanField(default=False)
    awarded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "core"
        db_table = "campaign_reviews"
        verbose_name = "Campaign Review"
        verbose_name_plural = "Campaign Reviews"

    def __str__(self):
        return f"Review by {self.user} on {self.novel} ({self.campaign})"

    @property
    def like_count(self):
        return self.likes.count()


# ---------- Campaign Review Like (reader-to-reader likes, toggle) ---------- #
class CampaignReviewLikeModel(BaseModel):
    review = models.ForeignKey(
        CampaignReviewModel,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    user = models.ForeignKey(
        "core.UserModel",
        on_delete=models.CASCADE,
        related_name="campaign_review_likes",
    )

    class Meta:
        app_label = "core"
        db_table = "campaign_review_likes"
        verbose_name = "Campaign Review Like"
        verbose_name_plural = "Campaign Review Likes"
        unique_together = ("review", "user")

    def __str__(self):
        return f"{self.user} likes {self.review_id}"
