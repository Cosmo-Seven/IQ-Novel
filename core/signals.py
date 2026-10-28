# core/signals.py  (သို့မဟုတ် existing signals file)

from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import ChapterModel
from helpers.webpush import notify_novel_subscribers


@receiver(post_save, sender=ChapterModel)
def notify_on_chapter_save(sender, instance, created, **kwargs):
    if not (instance.is_active and instance.approval_status == ChapterModel.ApprovalStatus.APPROVED and not instance.is_deleted):
        return

    novel = instance.novel
    chapter_url = f"/novels/detail/{novel.id}/"

    if created:
        notify_novel_subscribers(
            novel=novel,
            title=f"📖 {novel.title}",
            body=f"Chapter အသစ်: {instance.chapter_title}",
            url=chapter_url,
        )
    else:
        notify_novel_subscribers(
            novel=novel,
            title=f"✏️ {novel.title}",
            body=f"Chapter: {instance.chapter_title}",
            url=chapter_url,
        )