from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from decorators.login_decorator import login_required
from constants.message import UPDATE, DELETE

from helpers.filters import filter_querysets
from core.models import (
    SiteModel,
    UserModel,
    NovelModel,
    ChapterPurchaseModel,
    AuthorModel,
)
from django.contrib.auth.hashers import check_password
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from decorators.role_decorator import role_permission_required

def _author_for_user(user):
    return AuthorModel.objects.filter(user=user).first()

# ========================
# Dashboard
# ========================
@login_required("dashboard_login")
@role_permission_required("view_novelmodel")
def dashboard(request):
    novels = (
        NovelModel.objects.select_related("author")
        .annotate(
            sales_count=Count("chapters__purchased_by", distinct=True),
            gems_sold=Coalesce(Sum("chapters__purchased_by__gems_paid"), 0),
            revenue_mmk=Coalesce(Sum("chapters__purchased_by__sale_price_mmk"), 0),
        )
        .order_by("-revenue_mmk", "-created_at")
    )
    author = _author_for_user(request.user)
    if author and not request.user.is_staff:
        novels = novels.filter(author=author)

    filters = filter_querysets(
        request,
        novels,
        search_fields=["title", "author__name", "author__user__username"],
        date_field="created_at",
        order="-revenue_mmk",
    )

    totals = ChapterPurchaseModel.objects.filter(
        chapter__novel__in=filters["paginator"].object_list.values("id")
    ).aggregate(
        total_sales=Coalesce(Sum("sale_price_mmk"), 0),
        total_purchases=Count("id"),
        total_gems=Coalesce(Sum("gems_paid"), 0),
    )

    return render(
        request,
        "dashboard/novel_sales_list.html",
        {
            "novels": filters["page_obj"],
            "totals": totals,
            **filters,
        },
    )


# ========================
# Site Settings
# ========================
@login_required("dashboard_login")
def site_settings(request):
    site = SiteModel.objects.first()
    if request.method == "GET":
        context = {"site": site}
        return render(request, "dashboard/site_settings.html", context)
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        email = request.POST.get("email")
        favicon = request.FILES.get("favicon")
        logo = request.FILES.get("logo")
        if not site:
            site = SiteModel.objects.create(
                name=name,
                favicon=favicon,
                logo=logo,
                phone=phone,
                address=address,
                email=email,
            )
            site.save()
        else:
            site.name = name
            site.phone = phone
            site.address = address
            site.email = email
            if favicon:
                if site.favicon:
                    site.favicon.delete(save=False)
                site.favicon = favicon
            if logo:
                if site.logo:
                    site.logo.delete(save=False)
                site.logo = logo
            site.save()
            messages.success(request, UPDATE)
        return redirect("site_settings")


# ========================
# Page Not Found
# ========================
def page_not_found(request):
    return render(request, "dashboard/page_not_found.html", status=404)


# ========================
# Internal Server Error
# ========================
def internal_server_error(request):
    return render(request, "dashboard/internal_server_error.html", status=500)


# ========================
# Under Maintenance
# ========================
def under_maintenance(request):
    return render(request, "dashboard/under_maintenance.html", status=503)


# ========================
# Lock Screen
# ========================
def locked(request):
    request.session["is_locked"] = True
    return redirect("lock_screen")


def lock_screen(request):
    return render(request, "dashboard/lock_screen.html")


def unlock(request):
    if request.method == "POST":
        password = request.POST.get("password")

        user = UserModel.objects.get(email=request.user.email)
        if check_password(password, user.password):
            request.session["is_locked"] = False
            return redirect("dashboard")
        else:
            messages.error(request, "Incorrect password. Please try again.")
            return redirect("lock_screen")
    return redirect("lock_screen")
