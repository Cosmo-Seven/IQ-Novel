import uuid
from django.db import models
from helpers.translation import register_key
from models.base_models import BaseModel
from django.utils.text import slugify


# // Gem Model ------------------------------------------------------
class GemModel(BaseModel):
    gem_amount = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.gem_amount

    class Meta:
        app_label = "core"
        db_table = "gems"
        verbose_name = "Gem"
        verbose_name_plural = "Gems"

    def save(self, *args, **kwargs):
        key = slugify(self.gem_amount).replace("-", "_").lower()
        register_key(key, self.gem_amount)
        super().save(*args, **kwargs)

    @property
    def translation_key(self):
        return slugify(self.gem_amount).replace("-", "_").lower()


class GemOrderModel(BaseModel):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    user = models.ForeignKey(
        "core.UserModel",
        on_delete=models.CASCADE,
        related_name="gem_orders",
    )
    gem = models.ForeignKey(
        "core.GemModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    gem_amount = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    payment_screenshot = models.ImageField(
        upload_to="gem_order_screenshots",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    transaction_id = models.CharField(max_length=60, null=True, blank=True)
    approved_by = models.ForeignKey(
        "core.UserModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_gem_orders",
    )
    admin_note = models.TextField(blank=True, default="")

    class Meta:
        app_label = "core"
        db_table = "gem_orders"
        verbose_name = "Gem Order"
        verbose_name_plural = "Gem Orders"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - {self.user.email}"
