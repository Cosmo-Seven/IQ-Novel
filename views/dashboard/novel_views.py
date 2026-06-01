from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from core.models import (
    NovelModel,
    ChapterModel,
    GenreModel,
)
from helpers.filters import filter_querysets
from decorators.role_decorator import role_permission_required
from decorators.login_decorator import login_required
from django.db import transaction
from django.db.models import Max
from constants.message import CREATE, UPDATE, DELETE


# // Novel List ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required("view_novelmodel")
def novel_list(request):
    novels = NovelModel.objects.all().order_by("-created_at")

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


# // Novel Form ------------------------------------------------------
@login_required("dashboard_login")
@role_permission_required(["add_novelmodel", "change_novelmodel"])
def novel_form(request, pk=None):

    novel = None
    novel_chapters = NovelChapterModel.objects.none()

    if pk:
        novel = get_object_or_404(NovelModel, id=pk)
        novel_chapters = novel.chapters.all().order_by("-created_at")

    if request.method == "GET":
        return render(
            request,
            "dashboard/forms/novel_form.html",
            {
                "genres": GenreModel.objects.all().order_by("-created_at"),
                "novel": novel,
                "novel_chapters": novel_chapters,
            },
        )

    if request.method == "POST":
        title = request.POST.get("title")
        summery = request.POST.get("summery")
        genre = request.POST.get("genre")
        cover_image = request.FILES.get("cover_image")
        is_completed = request.POST.get("is_completed") == "on"
        is_popular = request.POST.get("is_popular") == "on"
        is_fanfic = request.POST.get("is_fanfic") == "on"

        if novel:
            novel.title = title
            novel.summery = summery
            novel.is_completed = is_completed
            novel.is_popular = is_popular
            novel.is_fanfic = is_fanfic
            if cover_image:
                novel.cover_image = cover_image
            novel.save()
            novel.genres.set([genre])

            messages.success(request, UPDATE)
        else:
            novel = NovelModel.objects.create(
                title=title,
                summery=summery,
                cover_image=cover_image,
                is_completed=is_completed,
                is_popular=is_popular,
                is_fanfic = is_fanfic,
                is_free = is_free
            )
            novel.genres.set([genre])
            messages.success(request, "Novel created!")

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
@role_permission_required("add_novelchaptermodel")
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
        NovelChapterModel.objects.create(
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
@role_permission_required("change_novelchaptermodel")
def novel_chapter_update(request, pk):
    chapter = get_object_or_404(NovelChapterModel, id=pk)
    novel = chapter.novel

    if request.method != "POST":
        return redirect("novel_update", novel.id)

    chapter_title = request.POST.get("chapter_title", "").strip()
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
@role_permission_required("delete_novelchaptermodel")
def novel_chapter_delete(request, pk):
    chapter = get_object_or_404(NovelChapterModel, id=pk)
    novel = chapter.novel

    if request.method != "POST":
        return redirect("novel_update", novel.id)

    with transaction.atomic():
        chapter.delete()

    messages.success(request, "Chapter deleted successfully")
    return redirect("novel_update", novel.id)