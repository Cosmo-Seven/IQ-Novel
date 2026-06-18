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
    GenreModel,
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
    
    genres = GenreModel.objects.all()
    
    if request.GET.get("genre_id"):
        novels = NovelModel.objects.filter(genre_id=request.GET.get("genre_id")).all()
    else:
        novels = NovelModel.objects.all()

    filters = filter_querysets(
        request,
        novels,
        search_fields=["title"],
        date_field="created_at",
    )


    return render(
        request,
        "dashboard/index.html",
        {
            "genres": genres,
            "novels": filters["page_obj"],
            **filters,
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
