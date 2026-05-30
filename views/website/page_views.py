from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from decorators.login_decorator import login_required
from django.contrib.auth import login, logout, authenticate
from helpers.mail import send_verification_email, send_reset_email
from core.models import (
    UserModel,
    SliderModel,
    GemModel,
    GemOrderModel,
    NovelModel,
    NovelChapterModel,
    ChapterPurchaseModel,
    BookmarkModel,
)

# ========================
# Index
# ========================
def index(request):
    sliders = SliderModel.objects.all().order_by("-created_at")
    novels = NovelModel.objects.all().order_by("-created_at")
    completed_novels = NovelModel.objects.filter(is_completed=True)
    popular_novels = NovelModel.objects.filter(is_popular=True)
    fanfic_novels = NovelModel.objects.filter(is_fanfic=True)
    free_novels = NovelModel.objects.filter(is_popular=True)
    context = {
        "sliders":sliders,
        "novels": novels,
        "completed_novels": completed_novels,
        "popular_novels": popular_novels,
        "fanfic_novels": fanfic_novels,
        "free_novels": free_novels,
    }
    return render(request, "website/index.html", context)


def gem(request):
    gems=GemModel.objects.all()
    context={
        "gems":gems
    }
    return render(request, "website/gem.html", context)

def novel_detail(request, id):
    novel = get_object_or_404(NovelModel, id=id)
    bookmarked = False
    if request.user.is_authenticated:
        bookmarked = BookmarkModel.objects.filter(user=request.user, novel=novel).exists()
    purchased_chapter_ids = []
    if request.user.is_authenticated:
        purchased_chapter_ids = list(
            request.user.chapter_purchases.values_list("chapter_id", flat=True)
        )

    context = {
        "novel": novel,
        "bookmarked": bookmarked,
        "purchased_chapter_ids": purchased_chapter_ids,
    }
    return render(request, "website/novel_detail.html", context)


def bookmark(request, id):
    novel = get_object_or_404(NovelModel, id=id)

    if not request.user.is_authenticated:
        messages.warning(request, "Please login to save bookmarks.")
        return redirect("login")

    if request.method == "POST":
        bookmark, created = BookmarkModel.objects.get_or_create(
            user=request.user,
            novel=novel,
        )
        if not created:
            bookmark.delete()
            messages.success(request, "Removed from bookmarks.")
        else:
            messages.success(request, "Saved to bookmarks.")

    return redirect("novel_detail", id=id)

@login_required("website_login")
def checkout(request, id):
    gem = get_object_or_404(GemModel, id=id)

    if request.method == "POST":
        payment_screenshot = request.FILES.get("payment_screenshot")
        if not payment_screenshot:
            messages.error(request, "Please upload your payment screenshot.")
        else:
            GemOrderModel.objects.create(
                user=request.user,
                gem=gem,
                gem_amount=gem.gem_amount,
                price=gem.price,
                payment_screenshot=payment_screenshot,
                status=GemOrderModel.STATUS_PENDING,
            )
            messages.success(
                request,
                "Your gem purchase request has been submitted. Admin will approve it before gems are added to your account.",
            )
            return redirect("website_profile")

    context = {
        "gem": gem
    }
    return render(request, "website/checkout.html", context)

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to view your profile.")
        return redirect("website_login")

    bookmarks = request.user.bookmarks.select_related("novel").all()
    gem_orders = request.user.gem_orders.select_related("gem").all().order_by("-created_at")
    return render(
        request,
        "website/profile.html",
        {"bookmarks": bookmarks, "gem_orders": gem_orders},
    )


@login_required("website_login")
def buy_chapter(request, id):
    chapter = get_object_or_404(NovelChapterModel, id=id)

    if chapter.is_free:
        messages.info(request, "This chapter is free.")
        return redirect("novel_detail", id=chapter.novel.id)

    if not request.user.is_authenticated:
        messages.warning(request, "Please login to buy chapters.")
        return redirect("website_login")

    if ChapterPurchaseModel.objects.filter(user=request.user, chapter=chapter).exists():
        messages.info(request, "You already own this chapter.")
        return redirect("novel_detail", id=chapter.novel.id)

    price = int(chapter.gem_price or 0)
    if request.user.gem < price:
        messages.error(request, "Insufficient gems. Please top up your gems.")
        return redirect("novel_detail", id=chapter.novel.id)

    if request.method == "POST":
        request.user.gem = max(0, request.user.gem - price)
        request.user.save()
        ChapterPurchaseModel.objects.create(user=request.user, chapter=chapter)
        messages.success(request, "Chapter purchased successfully. Gems deducted.")

    return redirect("novel_detail", id=chapter.novel.id)


def chapter_detail(request, id):
    chapter = get_object_or_404(NovelChapterModel, id=id)

    has_access = chapter.is_free
    if request.user.is_authenticated:
        has_access = has_access or ChapterPurchaseModel.objects.filter(
            user=request.user, chapter=chapter
        ).exists()

    if not has_access:
        messages.warning(request, "Please purchase this chapter to read it.")
        return redirect("novel_detail", id=chapter.novel.id)

    return render(request, "website/chapter_detail.html", {"chapter": chapter})

