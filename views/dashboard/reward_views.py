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
    rewards = RewardModel.objects.all().order_by("-created_at")
    filters = filter_querysets(
        request,
        rewards,
        search_fields=["user__username", "user__email"],
        date_field="created_at",
        order="-created_at",
    )

    return render(
        request,
        "dashboard/reward_list.html",
        {
            "rewards": filters["page_obj"],
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
            "dashboard/forms/reward_form.html",
            {"users": users, "reward": None},
        )

    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        amount = request.POST.get("amount")
        user_id = request.POST.get("user")

        if not all([start_date, end_date, amount]):
            messages.error(request, "All fields are required")
            return redirect("reward_create")

        try:
            amount = int(amount)
            if amount <= 0:
                messages.error(request, "Amount must be greater than 0")
                return redirect("reward_create")
        except ValueError:
            messages.error(request, "Invalid amount")
            return redirect("reward_create")

        user = None
        if user_id:
            user = get_object_or_404(UserModel, id=user_id)

        reward = RewardModel.objects.create(
            start_date=start_date,
            end_date=end_date,
            amount=amount,
            user=user,
        )
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
        amount = request.POST.get("amount")
        user_id = request.POST.get("user")

        if not all([start_date, end_date, amount]):
            messages.error(request, "All fields are required")
            return redirect("reward_update", pk)

        try:
            amount = int(amount)
            if amount <= 0:
                messages.error(request, "Amount must be greater than 0")
                return redirect("reward_update", pk)
        except ValueError:
            messages.error(request, "Invalid amount")
            return redirect("reward_update", pk)

        reward.start_date = start_date
        reward.end_date = end_date
        reward.amount = amount

        if user_id:
            user = get_object_or_404(UserModel, id=user_id)
            reward.user = user
        else:
            reward.user = None

        reward.save()
        messages.success(request, UPDATE)
        return redirect("reward_list")


# // Reward Delete ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("delete_rewardmodel")
def reward_delete(request, pk):
    reward = get_object_or_404(RewardModel, id=pk)
    if request.method == "POST":
        reward.delete()
        messages.success(request, DELETE)
        return redirect("reward_list")
