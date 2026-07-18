from django.db import models
from helpers.translation import register_key
from models.base_models import BaseModel
from enums.status import StatusEnum
from django.utils.text import slugify
from django.utils.timezone import now
from core.models import GenreModel

# ---------- Novel ---------- #
class NovelModel(BaseModel):
    class NovelType(models.TextChoices):
        FANFIC = 'fanfic', 'Fanfic'
        TRANSLATE = 'translate', 'Translate'
        OWN_CREATION = 'own_creation', 'Own Creation'

    title = models.CharField(max_length=255)

    cover_image = models.ImageField(upload_to='novels/')
    summary = models.TextField()

    novel_type = models.CharField(
        max_length=20,
        choices=NovelType.choices,
        default=NovelType.OWN_CREATION,
        null=True,
        blank=True,
    )

    genres = models.ManyToManyField(GenreModel, related_name="novels")
    status = models.CharField(max_length=10, choices=StatusEnum.choices, default=StatusEnum.ONGOING)

    author = models.ForeignKey(
        "core.AuthorModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="novels",
    )

    views = models.PositiveIntegerField(default=0)

    is_completed = models.BooleanField(default=False)
    delete_pending_approval = models.BooleanField(default=False)
    delete_requested_by = models.ForeignKey(
        "core.UserModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_novel_deletions",
    )
    delete_requested_at = models.DateTimeField(null=True, blank=True)
    delete_approved_by = models.ForeignKey(
        "core.UserModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_novel_deletions",
    )
    delete_approved_at = models.DateTimeField(null=True, blank=True)

    def request_delete(self, user):
        self.is_deleted = True
        self.deleted_at = now()
        self.deleted_by = user
        self.delete_pending_approval = True
        self.delete_requested_by = user
        self.delete_requested_at = now()
        self.delete_approved_by = None
        self.delete_approved_at = None
        self.save()
        return self

    def approve_delete(self, admin_user):
        if not self.delete_pending_approval:
            return False
        self.delete_pending_approval = False
        self.delete_approved_by = admin_user
        self.delete_approved_at = now()
        self.save(update_fields=["delete_pending_approval", "delete_approved_by", "delete_approved_at"])
        self.delete()
        return True

    def __str__(self):
        return self.title

    class Meta:
        app_label = "core"
        db_table = "novels"
        verbose_name = "Novel"
        verbose_name_plural = "Novels"

    def save(self, *args, **kwargs):
        key = slugify(self.title).replace("-", "_").lower()
        register_key(key, self.title)
        super().save(*args, **kwargs)

    @property
    def translation_key(self):
        return slugify(self.title).replace("-", "_").lower()