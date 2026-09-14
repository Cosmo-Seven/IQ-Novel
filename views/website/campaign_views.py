from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from decorators.login_decorator import login_required
from helpers.campaign_helper import toggle_like
from core.models import (
    ReviewCampaignModel,
    CampaignReviewModel,
    CampaignReviewLikeModel,
    NovelModel,
)


# ========================
# Campaign List
# ========================
def campaign_list(request):
    now = timezone.now()
    campaigns = ReviewCampaignModel.objects.filter(is_deleted=False).order_by("-start_date")

    context = {
        "campaigns": campaigns,
        "now": now,
    }
    return render(request, "website/campaign_list.html", context)


# ========================
# Campaign Detail (submit review + browse entries + like)
# ========================
def campaign_detail(request, id):
    campaign = get_object_or_404(ReviewCampaignModel, id=id, is_deleted=False)
    is_active = campaign.is_active_now()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.warning(request, "Please login to submit a review.")
            return redirect("website_login")

        if not is_active:
            messages.error(request, "This review campaign is not active right now.")
            return redirect("campaign_detail", id=campaign.id)

        novel_id = request.POST.get("novel_id")
        content = request.POST.get("content", "").strip()
        image = request.FILES.get("image")

        if not novel_id or not content or not image:
            messages.error(request, "Please choose a novel, write your review, and attach an image.")
            return redirect("campaign_detail", id=campaign.id)

        novel = get_object_or_404(NovelModel, id=novel_id)

        CampaignReviewModel.objects.create(
            campaign=campaign,
            novel=novel,
            user=request.user,
            image=image,
            content=content,
            created_by=request.user,
            updated_by=request.user,
        )
        messages.success(request, "Your review has been submitted to the campaign!")
        return redirect("campaign_detail", id=campaign.id)

    reviews = (
        campaign.reviews.filter(is_deleted=False, is_approved=True)
        .select_related("user", "novel")
        .prefetch_related("likes")
        .order_by("-created_at")
    )

    liked_review_ids = set()
    if request.user.is_authenticated:
        liked_review_ids = set(
            CampaignReviewLikeModel.objects.filter(
                review__campaign=campaign, user=request.user
            ).values_list("review_id", flat=True)
        )

    novels = NovelModel.objects.all().order_by("title")

    context = {
        "campaign": campaign,
        "is_active": is_active,
        "reviews": reviews,
        "liked_review_ids": liked_review_ids,
        "novels": novels,
    }
    return render(request, "website/campaign_detail.html", context)


# ========================
# Like / Unlike a campaign review
# ========================
@login_required("website_login")
def like_campaign_review(request, id):
    review = get_object_or_404(CampaignReviewModel, id=id, is_deleted=False)

    if request.method == "POST":
        toggle_like(review, request.user)

    return redirect("campaign_detail", id=review.campaign_id)
