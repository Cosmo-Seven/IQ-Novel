from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from core.models import ReviewCampaignModel, CampaignReviewModel
from decorators.role_decorator import role_permission_required
from decorators.login_decorator import login_required
from helpers.filters import filter_querysets
from helpers.campaign_helper import award_winner
from constants.message import CREATE, UPDATE, DELETE


# // Campaign List ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("view_reviewcampaignmodel")
def campaign_list(request):
    campaigns = ReviewCampaignModel.objects.all().order_by("-created_at")
    filters = filter_querysets(
        request,
        campaigns,
        search_fields=["title"],
        date_field="created_at",
        order="-created_at",
    )
    context = {"campaigns": filters["page_obj"], **filters}
    return render(request, "dashboard/campaign_list.html", context)


# // Campaign Create ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("add_reviewcampaignmodel")
def campaign_create(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        reward_amount = request.POST.get("reward_amount") or 0

        if not all([title, start_date, end_date]):
            messages.error(request, "Title, start date, and end date are required.")
            return redirect("campaign_list")

        try:
            reward_amount = int(reward_amount)
            if reward_amount <= 0:
                messages.error(request, "Reward amount must be greater than 0.")
                return redirect("campaign_list")
        except ValueError:
            messages.error(request, "Invalid reward amount.")
            return redirect("campaign_list")

        ReviewCampaignModel.objects.create(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            reward_amount=reward_amount,
            created_by=request.user,
            updated_by=request.user,
        )
        messages.success(request, CREATE)
        return redirect("campaign_list")


# // Campaign Update ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("change_reviewcampaignmodel")
def campaign_update(request, pk):
    campaign = get_object_or_404(ReviewCampaignModel, id=pk)

    if request.method == "POST":
        if campaign.is_awarded:
            messages.error(request, "This campaign has already been awarded and can no longer be edited.")
            return redirect("campaign_list")

        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        reward_amount = request.POST.get("reward_amount") or 0

        if not all([title, start_date, end_date]):
            messages.error(request, "Title, start date, and end date are required.")
            return redirect("campaign_list")

        try:
            reward_amount = int(reward_amount)
            if reward_amount <= 0:
                messages.error(request, "Reward amount must be greater than 0.")
                return redirect("campaign_list")
        except ValueError:
            messages.error(request, "Invalid reward amount.")
            return redirect("campaign_list")

        campaign.title = title
        campaign.description = description
        campaign.start_date = start_date
        campaign.end_date = end_date
        campaign.reward_amount = reward_amount
        campaign.updated_by = request.user
        campaign.save()
        messages.success(request, UPDATE)
        return redirect("campaign_list")


# // Campaign Delete ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("delete_reviewcampaignmodel")
def campaign_delete(request, pk):
    campaign = get_object_or_404(ReviewCampaignModel, id=pk)
    if request.method == "POST":
        campaign.soft_delete(user=request.user)
        messages.success(request, DELETE)
        return redirect("campaign_list")


# // Campaign Submissions (review + pick winner) ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("view_campaignreviewmodel")
def campaign_review_list(request, pk):
    campaign = get_object_or_404(ReviewCampaignModel, id=pk)
    reviews = (
        campaign.reviews.filter(is_deleted=False)
        .select_related("user", "novel")
        .prefetch_related("likes")
        .order_by("-created_at")
    )

    context = {
        "campaign": campaign,
        "reviews": reviews,
    }
    return render(request, "dashboard/campaign_review_list.html", context)


# // Award Winner ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("change_reviewcampaignmodel")
def campaign_award(request, pk, review_pk):
    campaign = get_object_or_404(ReviewCampaignModel, id=pk)
    review = get_object_or_404(CampaignReviewModel, id=review_pk)

    if request.method == "POST":
        success, message = award_winner(campaign, review, request.user)
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

    return redirect("campaign_review_list", pk=campaign.id)
