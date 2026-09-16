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


def award_review(review, admin_user):
    """
    Admin က review တစ်ခုချင်းစီကို winner အဖြစ်ရွေးပြီး reward (diamond) ပေးခြင်း
    - Winner အရေအတွက် ကန့်သတ်မထား - admin ကြိုက်သလောက် review ကို winner လုပ်နိုင်
    - Review တစ်ခုကို ထပ်ခါထပ်ခါ award လုပ်လို့ရရင် diamond နှစ်ဆင့်ပေါင်း ဝင်မှာဖြစ်လို့
      is_winner flag နဲ့ double-reward မဖြစ်အောင် lock ထားတယ်
    """
    if review.is_winner:
        return False, "This review has already been awarded."

    campaign = review.campaign

    review.is_winner = True
    review.awarded_at = timezone.now()
    review.save(update_fields=["is_winner", "awarded_at"])

    winner = review.user
    # Contest reward ဖြစ်တဲ့အတွက် (ဝယ်ထားတဲ့ paid gem မဟုတ်ဘဲ) promotion/free gem အနေနဲ့ ထည့်ပေး
    winner.free_gem = (winner.free_gem or 0) + campaign.reward_amount
    winner.save(update_fields=["free_gem"])

    return True, f"{winner.username} has been awarded {campaign.reward_amount} diamonds."


def unaward_review(review):
    """
    Admin မှားရွေးမိတဲ့ winner ကို ပြန်ဖျက်ခြင်း - ပေးထားတဲ့ diamond ကို ပြန်နှုတ် (0 အောက်မကျအောင်)
    """
    if not review.is_winner:
        return False, "This review is not currently a winner."

    campaign = review.campaign
    winner = review.user

    winner.free_gem = max(0, (winner.free_gem or 0) - campaign.reward_amount)
    winner.save(update_fields=["free_gem"])

    review.is_winner = False
    review.awarded_at = None
    review.save(update_fields=["is_winner", "awarded_at"])

    return True, "Winner status removed and diamonds reverted."
