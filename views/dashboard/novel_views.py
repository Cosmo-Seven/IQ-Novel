from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from core.models import (
    NovelModel,
    ChapterModel,
    ChapterPurchaseModel,
    GenreModel,
    AuthorModel,
)
from helpers.filters import filter_querysets
from decorators.role_decorator import role_permission_required
from decorators.login_decorator import login_required
from django.db import transaction
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from constants.message import CREATE, UPDATE, DELETE


def _author_for_user(user):
    return AuthorModel.objects.filter(user=user).first()


# // Novel List ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("view_novelmodel")
def novel_list(request):
    novels = NovelModel.objects.select_related("author").order_by("-created_at")
    author = _author_for_user(request.user)
    if author and not request.user.is_staff:
        novels = novels.filter(author=author)

    filters = filter_querysets(
        request,
        novels,
        search_fields=[],
        date_field="created_at",
        order="-created_at",
    )

    return render(
        request,
        "dashboard/novel_list.html",
        {
            "novels": filters["page_obj"],
            **filters,
        },
    )


@login_required("dashboard_login")
@role_permission_required("view_novelmodel")
def novel_sales_list(request):
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


# // Novel Form ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required(["add_novelmodel", "change_novelmodel"])
def novel_form(request, pk=None):

    novel = None
    novel_chapters = ChapterModel.objects.none()

    if pk:
        novel = get_object_or_404(NovelModel, id=pk)
        novel_chapters = novel.chapters.all().order_by("-created_at")
        author = _author_for_user(request.user)
        if author and not request.user.is_staff and novel.author_id != author.id:
            messages.error(request, "You can only edit your own novels.")
            return redirect("novel_list")

    if request.method == "GET":
        return render(
            request,
            "dashboard/forms/novel_form.html",
            {
                "genres": GenreModel.objects.all().order_by("-created_at"),
                "novel": novel,
                "selected_genres": list(novel.genres.values_list("id", flat=True)) if novel else [],
                "novel_chapters": novel_chapters,
            },
        )

    if request.method == "POST":
        if request.POST.get("bulk_update") == "1":
            if not novel:
                messages.error(request, "Please save the novel before applying bulk chapter updates.")
                return redirect("novel_list")

            selected_chapters = request.POST.getlist("selected_chapters")
            if not selected_chapters:
                messages.error(request, "Please select at least one chapter.")
                return redirect("novel_update", novel.id)

            try:
                bulk_gem_price = int(request.POST.get("bulk_gem_price") or 0)
            except ValueError:
                messages.error(request, "Invalid gem price value.")
                return redirect("novel_update", novel.id)

            with transaction.atomic():
                chapters = ChapterModel.objects.filter(id__in=selected_chapters, novel=novel)
                updated_count = chapters.count()
                if updated_count == 0:
                    messages.error(request, "No matching chapters found for update.")
                    return redirect("novel_update", novel.id)
                chapters.update(gem_price=bulk_gem_price, is_free=(bulk_gem_price == 0))

            messages.success(request, f"Updated gem price for {updated_count} chapter(s).")
            return redirect("novel_update", novel.id)

        title = request.POST.get("title")
        summary = request.POST.get("summary")
        genres = request.POST.getlist("genre")
        cover_image = request.FILES.get("cover_image")
        is_completed = request.POST.get("is_completed") == "on"
        is_popular = request.POST.get("is_popular") == "on"

        novel_type = request.POST.get("novel_type")

        if novel:
            author = _author_for_user(request.user)
            if author and not request.user.is_staff and novel.author_id != author.id:
                messages.error(request, "You can only edit your own novels.")
                return redirect("novel_list")

            novel.title = title
            novel.summary = summary
            novel.is_completed = is_completed
            novel.is_popular = is_popular
            novel.novel_type = novel_type
            if cover_image:
                novel.cover_image = cover_image
            novel.save()
            novel.genres.set(genres)
            messages.success(request, UPDATE)
        else:
            author = _author_for_user(request.user)
            if not author:
                messages.error(
                    request,
                    "Author profile not found. Please contact admin to set up your author account.",
                )
                return redirect("novel_list")

            novel = NovelModel.objects.create(
                title=title,
                summary=summary,
                cover_image=cover_image,
                is_completed=is_completed,
                is_popular=is_popular,
                novel_type = novel_type,
                author=author,
            )
            novel.genres.set(genres)
            messages.success(request, CREATE)

        return redirect("novel_update", novel.id)


# // Novel Delete ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("delete_novelmodel")
def novel_delete(request, pk):
    novel = get_object_or_404(NovelModel, id=pk)
    if request.method == "POST":
        if novel.cover_image:
            novel.cover_image.delete(save=False)
        novel.delete()
        messages.success(request, DELETE)
        return redirect("novel_list")


# // Novel Chapter Create ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("add_novelmodel")
def novel_chapter_create(request, novel_id):
    novel = get_object_or_404(NovelModel, id=novel_id)

    if request.method != "POST":
        return redirect("novel_update", novel.id)
    chapter_title = request.POST.get("chapters_title")
    content = request.POST.get("content")
    is_free = request.POST.get("is_free") == "on"
    gem_price = request.POST.get("gem_price", 0)

    # validation
    if not chapter_title:
        messages.error(request, "Chapter title is required")
        return redirect("novel_update", novel.id)

    if not content:
        messages.error(request, "Content is required")
        return redirect("novel_update", novel.id)

    try:
        gem_price = int(gem_price or 0)
    except ValueError:
        messages.error(request, "Invalid gem value")
        return redirect("novel_update", novel.id)

    if not is_free and gem_price <= 0:
        messages.error(request, "Paid chapter must have gem price")
        return redirect("novel_update", novel.id)

    with transaction.atomic():
        ChapterModel.objects.create(
            novel=novel,
            chapter_title=chapter_title,
            content=content,
            is_free=is_free,
            gem_price=0 if is_free else gem_price,
        )

    messages.success(request, "Chapter created successfully")
    return redirect("novel_update", novel.id)

# // Novel Chapter Update ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("change_novelmodel")
def novel_chapter_update(request, pk):
    chapter = get_object_or_404(ChapterModel, id=pk)
    novel = chapter.novel

    if request.method != "POST":
        return redirect("novel_update", novel.id)

    chapter_title = request.POST.get("chapters_title", "").strip()
    content = request.POST.get("content", "").strip()
    is_free = request.POST.get("is_free") == "on"

    # safe parse
    try:
        gem_price = int(request.POST.get("gem_price") or 0)
    except ValueError:
        messages.error(request, "Invalid gem price")
        return redirect("novel_update", novel.id)

    # validation
    if not chapter_title:
        messages.error(request, "Chapter title is required")
        return redirect("novel_update", novel.id)

    if not content:
        messages.error(request, "Content cannot be empty")
        return redirect("novel_update", novel.id)

    if not is_free and gem_price <= 0:
        messages.error(request, "Paid chapter must have gem price")
        return redirect("novel_update", novel.id)

    with transaction.atomic():
        chapter.chapter_title = chapter_title
        chapter.content = content
        chapter.is_free = is_free
        chapter.gem_price = 0 if is_free else gem_price

        chapter.save()

    messages.success(request, "Chapter updated successfully")
    return redirect("novel_update", novel.id)


# // Novel Chapter Delete ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("delete_novelmodel")
def novel_chapter_delete(request, pk):
    chapter = get_object_or_404(ChapterModel, id=pk)
    novel = chapter.novel

    if request.method != "POST":
        return redirect("novel_update", novel.id)

    with transaction.atomic():
        chapter.delete()

    messages.success(request, "Chapter deleted successfully")
    return redirect("novel_update", novel.id)

@login_required("dashboard_login")
@role_permission_required("view_chapterpurchasemodel")
def chapter_purchase_list(request):
    purchases = (
        ChapterPurchaseModel.objects
        .select_related("user", "chapter", "chapter__novel")
        .order_by("-created_at")
    )

    novel_id = request.GET.get("novel")
    if novel_id:
        purchases = purchases.filter(chapter__novel__id=novel_id)

    gem_type = request.GET.get("gem_type")
    if gem_type == "free":
        purchases = purchases.filter(free_gems_used__gt=0)
    elif gem_type == "paid":
        purchases = purchases.filter(paid_gems_used__gt=0)

    filters = filter_querysets(
        request,
        purchases,
        search_fields=["user__username", "user__email", "chapter__chapter_title", "chapter__novel__title"],
        date_field="created_at",
        order="-created_at",
    )

    totals = purchases.aggregate(
        total_purchases  = Count("id"),
        total_gems       = Coalesce(Sum("gems_paid"), 0),
        total_free_gems  = Coalesce(Sum("free_gems_used"), 0),
        total_paid_gems  = Coalesce(Sum("paid_gems_used"), 0),
        total_mmk        = Coalesce(Sum("sale_price_mmk"), 0),
    )

    novels = NovelModel.objects.all().order_by("title")

    return render(request, "dashboard/chapter_purchase_list.html", {
        "purchases"  : filters["page_obj"],
        "totals"     : totals,
        "novels"     : novels,
        "selected_novel"    : novel_id,
        "selected_gem_type" : gem_type,
        **filters,
    })