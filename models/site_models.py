from django.db import models
from models.base_models import BaseModel
from django.utils.text import slugify
from helpers.translation import register_key


class SiteModel(BaseModel):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    address = models.TextField(null=True)
    favicon = models.ImageField(upload_to="favicon")
    logo = models.ImageField(upload_to="logo", null=True)
    require_chapter_approval = models.BooleanField(
        default=False,
        help_text="If True, chapters uploaded by authors require admin approval. If False, chapters are auto-approved.",
    )

    @classmethod
    def get_settings(cls):
        site = cls.objects.first()
        if not site:
            site = cls.objects.create(name="IQ-Novel", require_chapter_approval=False)
        return site

    @property
    def auto_approve_chapters(self):
        return not self.require_chapter_approval

    def __str__(self):
        return self.name

    class Meta:
        app_label = "core"
        db_table = "sites"
        verbose_name = "Site"
        verbose_name_plural = "Sites"

    def save(self, *args, **kwargs):
        key = slugify(self.name).replace("-", "_").lower()
        register_key(key, self.name)
        super().save(*args, **kwargs)

    @property
    def translation_key(self):
        return slugify(self.name).replace("-", "_").lower()
