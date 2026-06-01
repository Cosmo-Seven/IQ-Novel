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
    ChapterModel,
    ChapterPurchaseModel,
    ChapterReadModel,
    BookmarkModel,
    AuthorModel,
    AuthorFollowModel,
)
from helpers.chapter_access import adjacent_chapters, chapter_has_access, novel_chapters_ordered

# ========================
# Index
# ========================
def index(request):
    sliders = SliderModel.objects.all().order_by("-created_at")
    novels = NovelModel.objects.select_related("author").order_by("-created_at")
    completed_novels = NovelModel.objects.select_related("author").filter(is_completed=True)
    popular_novels = NovelModel.objects.select_related("author").filter(is_popular=True)
    fanfic_novels = NovelModel.objects.select_related("author").filter(is_fanfic=True)
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
    novel = get_object_or_404(NovelModel.objects.select_related("author"), id=id)
    bookmarked = False
    is_following_author = False
    can_follow_author = False
    purchased_chapter_ids = []
    read_chapter_ids = []
    if request.user.is_authenticated:
        bookmarked = BookmarkModel.objects.filter(user=request.user, novel=novel).exists()
        purchased_chapter_ids = list(
            request.user.chapter_purchases.values_list("chapter_id", flat=True)
        )
        read_chapter_ids = list(
            request.user.chapter_reads.values_list("chapter_id", flat=True)
        )
        if novel.author:
            is_following_author = AuthorFollowModel.objects.filter(
                user=request.user, author=novel.author
            ).exists()
            can_follow_author = novel.author.user_id != request.user.id

    context = {
        "novel": novel,
        "bookmarked": bookmarked,
        "is_following_author": is_following_author,
        "can_follow_author": can_follow_author,
        "chapters_ordered": novel_chapters_ordered(novel),
        "purchased_chapter_ids": purchased_chapter_ids,
        "read_chapter_ids": read_chapter_ids,
    }
    return render(request, "website/novel_detail.html", context)


def author_profile(request, id):
    author = get_object_or_404(
        AuthorModel.objects.select_related("user"),
        id=id,
    )
    novels = author.novels.all().order_by("-created_at")
    followers = (
        author.follower_records.select_related("user")
        .order_by("-created_at")
    )
    follower_count = followers.count()
    is_following = False
    can_follow = False
    if request.user.is_authenticated:
        is_following = AuthorFollowModel.objects.filter(
            user=request.user, author=author
        ).exists()
        can_follow = author.user_id != request.user.id

    return render(
        request,
        "website/author_profile.html",
        {
            "author": author,
            "novels": novels,
            "followers": followers,
            "follower_count": follower_count,
            "is_following": is_following,
            "can_follow": can_follow,
        },
    )


@login_required("website_login")
def follow_author(request, id):
    author = get_object_or_404(AuthorModel, id=id)

    if author.user_id == request.user.id:
        messages.warning(request, "You cannot follow yourself.")
        return redirect("author_profile", id=author.id)

    if request.method == "POST":
        follow, created = AuthorFollowModel.objects.get_or_create(
            user=request.user,
            author=author,
        )
        if not created:
            follow.delete()
            messages.success(request, f"Unfollowed {author.display_name}.")
        else:
            messages.success(request, f"You are now following {author.display_name}.")

    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("author_profile", id=author.id)


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
    chapter_purchases = request.user.chapter_purchases.select_related(
        "chapter", "chapter__novel"
    ).all().order_by("-created_at")
    
    # Get distinct novels from the user's purchased chapters
    purchased_novels = NovelModel.objects.filter(
        chapters__purchased_by__user=request.user
    ).distinct()

    # Author stats: follower count & novel count
    author_profile = None
    follower_count = 0
    novel_count = 0
    following_authors = []
    if hasattr(request.user, "author_profile"):
        author_profile = request.user.author_profile
        follower_count = author_profile.follower_records.count()
        novel_count = author_profile.novels.count()

    # Authors the user is following
    following_authors = (
        AuthorFollowModel.objects.filter(user=request.user)
        .select_related("author", "author__user")
        .order_by("-created_at")
    )

    return render(
        request,
        "website/profile.html",
        {
            "bookmarks": bookmarks,
            "gem_orders": gem_orders,
            "chapter_purchases": chapter_purchases,
            "purchased_novels": purchased_novels,
            "author_profile": author_profile,
            "follower_count": follower_count,
            "novel_count": novel_count,
            "following_authors": following_authors,
        },
    )


@login_required("website_login")
def buy_chapter(request, id):
    chapter = get_object_or_404(ChapterModel, id=id)

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
        from helpers.gem_pricing import gem_unit_price_mmk, gems_to_mmk

        author = chapter.novel.author
        revenue_share_percent = author.revenue_share_percent if author else 0
        unit_price = gem_unit_price_mmk()
        sale_price_mmk = gems_to_mmk(price)
        author_share_mmk = author.calculate_share(sale_price_mmk) if author else 0

        request.user.gem = max(0, request.user.gem - price)
        request.user.save()
        ChapterPurchaseModel.objects.create(
            user=request.user,
            chapter=chapter,
            gems_paid=price,
            sale_price_mmk=sale_price_mmk,
            author_share_mmk=author_share_mmk,
            gem_unit_price_mmk=unit_price,
            revenue_share_percent=revenue_share_percent,
        )
        messages.success(request, "Chapter purchased successfully. Gems deducted.")

    return redirect("novel_detail", id=chapter.novel.id)


def chapter_detail(request, id):
    chapter = get_object_or_404(ChapterModel.objects.select_related("novel"), id=id)

    if not chapter_has_access(request.user, chapter):
        messages.warning(request, "Please purchase this chapter to read it.")
        return redirect("novel_detail", id=chapter.novel.id)

    if request.user.is_authenticated:
        ChapterReadModel.objects.get_or_create(user=request.user, chapter=chapter)

    prev_chapter, next_chapter = adjacent_chapters(chapter)

    purchased_chapter_ids = []
    if request.user.is_authenticated:
        purchased_chapter_ids = list(
            request.user.chapter_purchases.values_list("chapter_id", flat=True)
        )

    return render(
        request,
        "website/chapter_detail.html",
        {
            "chapter": chapter,
            "prev_chapter": prev_chapter,
            "next_chapter": next_chapter,
            "purchased_chapter_ids": purchased_chapter_ids,
        },
    )

