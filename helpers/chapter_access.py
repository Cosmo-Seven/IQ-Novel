from core.models import ChapterPurchaseModel


def chapter_has_access(user, chapter):
    if chapter.is_free:
        return True
    if user.is_authenticated:
        return ChapterPurchaseModel.objects.filter(user=user, chapter=chapter).exists()
    return False


def novel_chapters_ordered(novel):
    return list(novel.chapters.order_by("created_at", "id"))


def adjacent_chapters(chapter):
    chapters = novel_chapters_ordered(chapter.novel)
    chapter_ids = [c.id for c in chapters]
    try:
        index = chapter_ids.index(chapter.id)
    except ValueError:
        return None, None
    prev_chapter = chapters[index - 1] if index > 0 else None
    next_chapter = chapters[index + 1] if index < len(chapters) - 1 else None
    return prev_chapter, next_chapter
