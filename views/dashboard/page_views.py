from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from decorators.login_decorator import login_required
from constants.message import UPDATE, DELETE

from django.db.models import Count, Sum
from core.models import (
    SiteModel,
    UserModel,
    NovelModel,
    ChapterPurchaseModel,
    AuthorModel,
)
from django.contrib.auth.hashers import check_password
from decorators.role_decorator import role_permission_required

def _author_for_user(user):
    return AuthorModel.objects.filter(user=user).first()

# ========================
# Dashboard
# ========================
@login_required("dashboard_login")
def dashboard(request):
    is_admin = request.user.is_staff or request.user.is_superuser
    author = None if is_admin else _author_for_user(request.user)

    purchases = ChapterPurchaseModel.objects.filter(
        is_deleted=False,
        chapter__is_deleted=False,
        chapter__novel__is_deleted=False,
    )

    if is_admin:
        user_count = UserModel.objects.filter(is_deleted=False).count()
        author_count = AuthorModel.objects.filter(is_deleted=False).count()
        novel_count = NovelModel.objects.filter(is_deleted=False).count()
    else:
        if author:
            novel_count = NovelModel.objects.filter(
                is_deleted=False, author=author
            ).count()
            purchases = purchases.filter(chapter__novel__author=author)
        else:
            novel_count = 0
            purchases = purchases.none()
        author_count = None

    purchase_totals = purchases.aggregate(
        chapter_purchase=Count("pk"),
        buyer_count=Count("user_id", distinct=True),
        gem_sales=Sum("paid_gems_used"),
        coupon_sales=Sum("free_gems_used"),
        sales_amount_mmk=Sum("sale_price_mmk"),
        author_share_mmk=Sum("author_share_mmk"),
    )

    return render(
        request,
        "dashboard/index.html",
        {
            "is_admin": is_admin,
            "user_count": (
                user_count if is_admin else purchase_totals["buyer_count"]
            ),
            "chapter_purchase": purchase_totals["chapter_purchase"],
            "gem_sales": purchase_totals["gem_sales"] or 0,
            "coupon_sales": purchase_totals["coupon_sales"] or 0,
            "sales_amount_mmk": purchase_totals["sales_amount_mmk"] or 0,
            "author_share_mmk": purchase_totals["author_share_mmk"] or 0,
            "author_count": author_count,
            "novel_count": novel_count,
        },
    )


# ========================
# Site Settings
# ========================
@login_required("dashboard_login")
@role_permission_required("view_sitemodel")
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
        require_chapter_approval = request.POST.get("require_chapter_approval") == "on"
        if not site:
            site = SiteModel.objects.create(
                name=name,
                favicon=favicon,
                logo=logo,
                phone=phone,
                address=address,
                email=email,
                require_chapter_approval=require_chapter_approval,
            )
            site.save()
        else:
            site.name = name
            site.phone = phone
            site.address = address
            site.email = email
            site.require_chapter_approval = require_chapter_approval
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
