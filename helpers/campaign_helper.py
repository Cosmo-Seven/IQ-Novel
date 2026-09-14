# helpers/campaign_helper.py

from django.utils import timezone
from core.models import ReviewCampaignModel, CampaignReviewLikeModel


def get_active_campaigns():
    """
    Admin က start/end date သတ်မှတ်ထားတဲ့ campaign တွေထဲက
    အခုလက်ရှိအချိန်မှာ active ဖြစ်နေတာတွေချည်း ပြန်ပေး
    """
    now = timezone.now()
    return ReviewCampaignModel.objects.filter(
        is_deleted=False,
        start_date__lte=now,
        end_date__gte=now,
    ).order_by("-start_date")


def toggle_like(review, user):
    """
    User တစ်ယောက်ဟာ review တစ်ခုကို like/unlike လုပ်တာကို toggle
    return: (liked: bool, like_count: int)
    """
    like, created = CampaignReviewLikeModel.objects.get_or_create(
        review=review,
        user=user,
    )
    if not created:
        like.delete()
        return False, review.likes.count()

    return True, review.likes.count()


def award_winner(campaign, review, admin_user):
    """
    Admin က campaign တစ်ခုအတွက် winner review ရွေးပြီး reward (diamond) ပေးခြင်း
    - review ဟာ campaign ရဲ့ own review ဖြစ်ရမယ်
    - campaign တစ်ခုကို တစ်ကြိမ်ပဲ award လုပ်ခွင့်ရှိတယ် (double reward မဖြစ်အောင်)
    """
    if campaign.is_awarded:
        return False, "This campaign has already been awarded."

    if review.campaign_id != campaign.id:
        return False, "This review does not belong to the selected campaign."

    campaign.winner_review = review
    campaign.is_awarded = True
    campaign.awarded_at = timezone.now()
    campaign.awarded_by = admin_user
    campaign.save(update_fields=[
        "winner_review", "is_awarded", "awarded_at", "awarded_by",
    ])

    winner = review.user
    # Contest reward ဖြစ်တဲ့အတွက် (ဝယ်ထားတဲ့ paid gem မဟုတ်ဘဲ) promotion/free gem အနေနဲ့ ထည့်ပေး
    winner.free_gem = (winner.free_gem or 0) + campaign.reward_amount
    winner.save(update_fields=["free_gem"])

    return True, "Winner has been awarded successfully."
