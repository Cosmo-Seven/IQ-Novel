from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.db.models import F, Q, Count
from decorators.login_decorator import login_required
from django.contrib.auth import login, logout, authenticate
from helpers.mail import send_verification_email, send_reset_email
from core.models import (
    UserModel,
    SliderModel,
    GemModel,
    GenreModel,
    GemOrderModel,
    NovelModel,
    ChapterModel,
    ChapterPurchaseModel,
    ChapterReadModel,
    BookmarkModel,
    AuthorModel,
    AuthorFollowModel,
    CommentModel,
    NovelViewModel,
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
    genres = GenreModel.objects.all()
    context = {
        "sliders":sliders,
        "novels": novels,
        "completed_novels": completed_novels,
        "popular_novels": popular_novels,
        "fanfic_novels": fanfic_novels,
        "free_novels": free_novels,
        "genres":genres
    }
    return render(request, "website/index.html", context)


def gem(request):
    gems=GemModel.objects.all()
    context={
        "gems":gems
    }
    return render(request, "website/gem.html", context)

def novel(request):
    novels = NovelModel.objects.all().order_by("-created_at")
    genres = GenreModel.objects.annotate(novel_count=Count('novels')) 
    
    search_query = request.GET.get('q', '')
    genre_filter = request.GET.get('genre', '')
    sort_filter = request.GET.get('sort', '')
    
    # UUID-based genre id — no int() cast
    active_genre_id = genre_filter if genre_filter else None

    if search_query:
        novels = novels.filter(
            Q(title__icontains=search_query) |
            Q(genres__name__icontains=search_query)
        )
        
    if active_genre_id:
        novels = novels.filter(genres__id=active_genre_id)

    if sort_filter == 'popular':
        novels = novels.filter(is_popular=True)
    elif sort_filter == 'new':
        novels = novels.order_by("-created_at")

    novels = novels.distinct()

    # Pagination — 20 per page
    from django.core.paginator import Paginator
    paginator = Paginator(novels, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "novels": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
        "genres": genres,
        "search_query": search_query,
        "active_genre_id": active_genre_id,
        "sort_filter": sort_filter,
    }
    return render(request, "website/novel.html", context)

# @login_required("website_login")
def novel_detail(request, id):
    novel = get_object_or_404(NovelModel.objects.select_related("author"), id=id)

    if request.method == "POST":
        comment_text = request.POST.get("comment_text", "").strip()
        if comment_text:
            CommentModel.objects.create(
                user=request.user,
                novel=novel,
                content=comment_text,
                created_by=request.user,
                updated_by=request.user,
            )
            messages.success(request, "Your comment has been posted.")
            return redirect("novel_detail", id=id)
        messages.error(request, "Please write a comment before submitting.")

    if request.method == "GET" and request.user.is_authenticated:
        novel_view, created = NovelViewModel.objects.get_or_create(
            user=request.user,
            novel=novel,
        )
        if created:
            NovelModel.objects.filter(id=novel.id).update(views=F("views") + 1)
            novel.refresh_from_db(fields=["views"])

    bookmarked = False
    downloaded = False
    is_following_author = False
    can_follow_author = False
    purchased_chapter_ids = []
    read_chapter_ids = []
    if request.user.is_authenticated:
        bookmarked = BookmarkModel.objects.filter(user=request.user, novel=novel).exists()
        from core.models import DownloadModel
        downloaded = DownloadModel.objects.filter(user=request.user, novel=novel).exists()
        purchased_chapter_ids = set(
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
    else:
        purchased_chapter_ids = set()
        read_chapter_ids = []

    purchasable_chapters = []
    for chapter in novel_chapters_ordered(novel):
        if len(purchasable_chapters) >= 10:
            break
        if chapter.is_free or chapter.id in purchased_chapter_ids:
            continue
        purchasable_chapters.append(chapter)

    comments = novel.comments.filter(is_deleted=False, is_approved=True).select_related("user").order_by("-created_at")
    related_novels = NovelModel.objects.filter(
        genres__in=novel.genres.all()
    ).exclude(id=novel.id).distinct().select_related("author").order_by("-views")[:6]

    if not related_novels:
        related_novels = NovelModel.objects.filter(
            author=novel.author
        ).exclude(id=novel.id).select_related("author").order_by("-views")[:6]

    context = {
        "novel": novel,
        "bookmarked": bookmarked,
        "downloaded": downloaded,
        "is_following_author": is_following_author,
        "can_follow_author": can_follow_author,
        "chapters_ordered": novel_chapters_ordered(novel),
        "purchased_chapter_ids": purchased_chapter_ids,
        "read_chapter_ids": read_chapter_ids,
        "buy_ten_count": len(purchasable_chapters),
        "buy_ten_total": sum(int(chapter.gem_price or 0) for chapter in purchasable_chapters),
        "comments": comments,
        "related_novels": related_novels,
    }
    return render(request, "website/novel_detail.html", context)

def genre_list(request):
    genres = GenreModel.objects.annotate(novel_count=Count('novels')).order_by('name')
    context = {
        "genres": genres,
    }
    return render(request, "website/genre.html", context)

@login_required("website_login")
def edit_comment(request, id):
    comment = get_object_or_404(CommentModel, id=id, is_deleted=False)
    if comment.user != request.user:
        messages.error(request, "You can only edit your own comment.")
        return redirect("novel_detail", id=comment.novel.id)

    if request.method == "POST":
        comment_text = request.POST.get("comment_text", "").strip()
        if comment_text:
            comment.content = comment_text
            comment.updated_by = request.user
            comment.save()
            messages.success(request, "Comment updated successfully.")
        else:
            messages.error(request, "Please enter a comment before saving.")

    return redirect("novel_detail", id=comment.novel.id)


@login_required("website_login")
def delete_comment(request, id):
    comment = get_object_or_404(CommentModel, id=id, is_deleted=False)
    if comment.user != request.user:
        messages.error(request, "You can only delete your own comment.")
        return redirect("novel_detail", id=comment.novel.id)

    if request.method == "POST":
        comment.soft_delete(user=request.user)
        messages.success(request, "Comment deleted successfully.")

    return redirect("novel_detail", id=comment.novel.id)


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

@login_required("website_login")
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

from django.http import JsonResponse
@login_required("website_login")
def toggle_download(request, id):
    novel = get_object_or_404(NovelModel, id=id)

    if request.method == "POST":
        from core.models import DownloadModel
        download, created = DownloadModel.objects.get_or_create(
            user=request.user,
            novel=novel,
        )
        if not created:
            download.delete()
            return JsonResponse({"status": "removed", "message": "Removed from offline downloads."})
        else:
            return JsonResponse({"status": "added", "message": "Downloaded for offline reading."})

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)

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

    # Reading list: distinct novels the user has started reading (via chapter reads)
    from django.db.models import Max
    reading_list = (
        NovelModel.objects.filter(
            chapters__read_by__user=request.user
        )
        .annotate(last_read_at=Max("chapters__read_by__created_at"))
        .order_by("-last_read_at")
        .distinct()
    )

    # Downloaded Novels
    from core.models import DownloadModel
    downloaded_novels = DownloadModel.objects.filter(user=request.user).select_related("novel").order_by("-created_at")

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
            "reading_list": reading_list,
            "downloaded_novels": downloaded_novels,
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


@login_required("website_login")
def buy_ten_chapters(request, id):
    novel = get_object_or_404(NovelModel.objects.select_related("author"), id=id)
    purchased_chapter_ids = set(
        request.user.chapter_purchases.values_list("chapter_id", flat=True)
    )
    chapters_to_buy = []
    for chapter in novel_chapters_ordered(novel):
        if len(chapters_to_buy) >= 10:
            break
        if chapter.is_free or chapter.id in purchased_chapter_ids:
            continue
        chapters_to_buy.append(chapter)

    if not chapters_to_buy:
        messages.info(request, "No chapters available to purchase.")
        return redirect("novel_detail", id=novel.id)

    total_price = sum(int(chapter.gem_price or 0) for chapter in chapters_to_buy)
    if request.user.gem < total_price:
        messages.error(request, "Insufficient gems. Please top up your gems.")
        return redirect("novel_detail", id=novel.id)

    if request.method == "POST":
        from helpers.gem_pricing import gem_unit_price_mmk, gems_to_mmk

        author = novel.author
        revenue_share_percent = author.revenue_share_percent if author else 0
        unit_price = gem_unit_price_mmk()

        for chapter in chapters_to_buy:
            price = int(chapter.gem_price or 0)
            sale_price_mmk = gems_to_mmk(price)
            author_share_mmk = author.calculate_share(sale_price_mmk) if author else 0
            ChapterPurchaseModel.objects.create(
                user=request.user,
                chapter=chapter,
                gems_paid=price,
                sale_price_mmk=sale_price_mmk,
                author_share_mmk=author_share_mmk,
                gem_unit_price_mmk=unit_price,
                revenue_share_percent=revenue_share_percent,
            )

        request.user.gem = max(0, request.user.gem - total_price)
        request.user.save(update_fields=["gem"])
        messages.success(
            request,
            f"{len(chapters_to_buy)} chapters purchased successfully. Gems deducted.",
        )

    return redirect("novel_detail", id=novel.id)


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

def contact_page(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        if not name or not email or not message:
            messages.error(request, "Please fill all fields")
            return redirect('contact_page')
        
        messages.success(request, "We will touch you soon")
        return redirect('contact_page')
        
    return render(request, "website/contact.html")

def page404(request):
    return render(request, "website/page404.html")