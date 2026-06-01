import calendar
from datetime import date

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from constants.message import CREATE, DELETE, UPDATE
from core.models import AuthorModel, AuthorSalaryModel, ChapterPurchaseModel, UserModel
from decorators.login_decorator import login_required
from decorators.role_decorator import role_permission_required
from helpers.filters import filter_querysets


def _month_bounds(year, month):
    start = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end = date(year, month, last_day)
    return start, end


def _purchases_for_author_month(author, year, month):
    start, end = _month_bounds(year, month)
    return ChapterPurchaseModel.objects.filter(
        chapter__novel__author=author,
        created_at__date__gte=start,
        created_at__date__lte=end,
    )


def calculate_monthly_amount_mmk(author, year, month):
    return (
        _purchases_for_author_month(author, year, month).aggregate(
            total=Sum("author_share_mmk")
        )["total"]
        or 0
    )


def sync_author_salary(author, year, month):
    total_amount_mmk = calculate_monthly_amount_mmk(author, year, month)
    salary, created = AuthorSalaryModel.objects.get_or_create(
        author=author,
        year=year,
        month=month,
        defaults={"total_amount_mmk": total_amount_mmk},
    )
    if not created and salary.status == AuthorSalaryModel.STATUS_PENDING:
        salary.total_amount_mmk = total_amount_mmk
        salary.save(update_fields=["total_amount_mmk", "updated_at"])
    return salary


@login_required("dashboard_login")
@role_permission_required("view_authormodel")
def author_list(request):
    authors = AuthorModel.objects.select_related("user").order_by("-created_at")
    filters = filter_querysets(
        request,
        authors,
        search_fields=["name", "user__username", "user__email"],
        date_field="created_at",
        order="-created_at",
    )
    eligible_users = UserModel.objects.filter(author_profile__isnull=True).order_by(
        "username"
    )
    return render(
        request,
        "dashboard/author_list.html",
        {
            "authors": filters["page_obj"],
            "eligible_users": eligible_users,
            **filters,
        },
    )


@login_required("dashboard_login")
@role_permission_required("add_authormodel")
def author_create(request):
    if request.method != "POST":
        return redirect("author_list")

    user_id = request.POST.get("user")
    name = (request.POST.get("name") or "").strip()
    bio = request.POST.get("bio", "")
    website = request.POST.get("website") or None
    profile = request.FILES.get("profile")

    try:
        percent = int(request.POST.get("revenue_share_percent") or 0)
    except ValueError:
        messages.error(request, "Invalid revenue share percent.")
        return redirect("author_list")

    if percent < 0 or percent > 100:
        messages.error(request, "Revenue share must be between 0 and 100.")
        return redirect("author_list")

    user = get_object_or_404(UserModel, id=user_id)
    if AuthorModel.objects.filter(user=user).exists():
        messages.error(request, "This user already has an author profile.")
        return redirect("author_list")

    AuthorModel.objects.create(
        user=user,
        name=name or user.username,
        bio=bio,
        website=website,
        profile=profile,
        revenue_share_percent=percent,
    )
    messages.success(request, CREATE)
    return redirect("author_list")


@login_required("dashboard_login")
@role_permission_required("change_authormodel")
def author_update(request, pk):
    author = get_object_or_404(AuthorModel, id=pk)
    if request.method != "POST":
        return redirect("author_list")

    author.name = (request.POST.get("name") or "").strip() or author.user.username
    author.bio = request.POST.get("bio", "")
    author.website = request.POST.get("website") or None

    try:
        percent = int(request.POST.get("revenue_share_percent") or 0)
    except ValueError:
        messages.error(request, "Invalid revenue share percent.")
        return redirect("author_list")

    if percent < 0 or percent > 100:
        messages.error(request, "Revenue share must be between 0 and 100.")
        return redirect("author_list")

    author.revenue_share_percent = percent

    if request.FILES.get("profile"):
        if author.profile:
            author.profile.delete(save=False)
        author.profile = request.FILES.get("profile")

    author.save()
    messages.success(request, UPDATE)
    return redirect("author_list")


@login_required("dashboard_login")
@role_permission_required("delete_authormodel")
def author_delete(request, pk):
    author = get_object_or_404(AuthorModel, id=pk)
    if request.method == "POST":
        if author.profile:
            author.profile.delete(save=False)
        author.delete()
        messages.success(request, DELETE)
    return redirect("author_list")


@login_required("dashboard_login")
@role_permission_required("view_authorsalarymodel")
def author_salary_list(request):
    today = timezone.localdate()
    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
    except ValueError:
        year, month = today.year, today.month

    if month < 1 or month > 12:
        month = today.month

    authors = AuthorModel.objects.select_related("user").order_by("name", "user__username")
    rows = []
    for author in authors:
        sync_author_salary(author, year, month)
        salary = AuthorSalaryModel.objects.get(author=author, year=year, month=month)
        purchases = _purchases_for_author_month(author, year, month)
        sales_gems = purchases.aggregate(total=Sum("gems_paid"))["total"] or 0
        sales_amount_mmk = purchases.aggregate(total=Sum("sale_price_mmk"))["total"] or 0
        rows.append(
            {
                "author": author,
                "salary": salary,
                "sales_gems": sales_gems,
                "sales_amount_mmk": sales_amount_mmk,
                "purchase_count": purchases.count(),
            }
        )

    return render(
        request,
        "dashboard/author_salary_list.html",
        {
            "rows": rows,
            "year": year,
            "month": month,
            "month_name": calendar.month_name[month],
        },
    )


@login_required("dashboard_login")
@role_permission_required("change_authorsalarymodel")
def author_salary_mark_paid(request, pk):
    salary = get_object_or_404(AuthorSalaryModel, id=pk)
    if request.method == "POST":
        salary.status = AuthorSalaryModel.STATUS_PAID
        salary.paid_at = timezone.now()
        salary.note = request.POST.get("note", salary.note)
        salary.save()
        messages.success(request, "Salary marked as paid.")
    return redirect(
        f"{reverse('author_salary_list')}?year={salary.year}&month={salary.month}"
    )
