from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from core.models import RewardModel, DailyRewardModel, UserModel
from decorators.role_decorator import role_permission_required
from decorators.login_decorator import login_required
from helpers.filters import filter_querysets
from constants.message import CREATE, UPDATE, DELETE


# // Reward List ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("view_rewardmodel")
def reward_list(request):
    rewards = (
        RewardModel.objects.all()
        .prefetch_related("users")
        .distinct()
        .order_by("-created_at")
    )
    filters = filter_querysets(
        request,
        rewards,
        search_fields=["users__username", "users__email"],
        date_field="created_at",
        order="-created_at",
    )

    return render(
        request,
        "dashboard/reward_list.html",
        {
            "rewards": filters["page_obj"],
            "users": UserModel.objects.all().order_by("username"),
            **filters,
        },
    )


# // Reward Create ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("add_rewardmodel")
def reward_create(request):
    if request.method == "GET":
        users = UserModel.objects.all().order_by("username")
        return render(
            request,
            "dashboard/reward_list.html",
            {"users": users, "reward": None},
        )

    if request.method == "POST":
        start_date  = request.POST.get("start_date")
        end_date    = request.POST.get("end_date")
        user_ids    = [u for u in request.POST.getlist("users") if u and u != "all"]
        reward_type = request.POST.get("reward_type", "gem_gift")

        # date validation အရင်
        if not all([start_date, end_date]):
            messages.error(request, "Start date and end date are required")
            return redirect("reward_create")

        # amount က reward_type ပေါ် မူတည်
        if reward_type == "gem_gift":
            try:
                amount = int(request.POST.get("amount") or 0)
                if amount <= 0:
                    messages.error(request, "Amount must be greater than 0")
                    return redirect("reward_create")
            except ValueError:
                messages.error(request, "Invalid amount")
                return redirect("reward_create")
        else:
            amount = 0  # free_read / discount_read မှာ amount မလို

        reward = RewardModel.objects.create(
            start_date=start_date,
            end_date=end_date,
            amount=amount,
            reward_type=reward_type,
        )
        if user_ids:
            reward.users.set(UserModel.objects.filter(id__in=user_ids))
        messages.success(request, CREATE)
        return redirect("reward_list")


# // Reward Update ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("change_rewardmodel")
def reward_update(request, pk):
    reward = get_object_or_404(RewardModel, id=pk)

    if request.method == "GET":
        users = UserModel.objects.all().order_by("username")
        return render(
            request,
            "dashboard/forms/reward_form.html",
            {"reward": reward, "users": users},
        )

    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        user_ids = [u for u in request.POST.getlist("users") if u and u != "all"]
        reward_type = request.POST.get("reward_type", "gem_gift")

        # date validation အရင်
        if not all([start_date, end_date]):
            messages.error(request, "Start date and end date are required")
            return redirect("reward_update", pk)

        # amount က reward_type ပေါ် မူတည် (gem_gift မှသာ amount လို)
        if reward_type == "gem_gift":
            try:
                amount = int(request.POST.get("amount") or 0)
                if amount <= 0:
                    messages.error(request, "Amount must be greater than 0")
                    return redirect("reward_update", pk)
            except ValueError:
                messages.error(request, "Invalid amount")
                return redirect("reward_update", pk)
        else:
            amount = 0  # free_read / discount_read မှာ amount မလို

        reward.start_date = start_date
        reward.end_date = end_date
        reward.reward_type = reward_type
        reward.amount = amount
        reward.save()

        reward.users.set(UserModel.objects.filter(id__in=user_ids))

        messages.success(request, UPDATE)
        return redirect("reward_list")


# // Reward Delete ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("delete_rewardmodel")
def reward_delete(request, pk):
    if request.method != "POST":
        messages.warning(request, "Please use the delete confirmation to remove a reward.")
        return redirect("reward_list")

    reward = get_object_or_404(RewardModel, id=pk)
    reward.delete()
    messages.success(request, DELETE)
    return redirect("reward_list")
