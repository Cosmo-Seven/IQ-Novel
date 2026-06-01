from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from models.base_models import BaseModel


# ---------- Author ---------- #
class AuthorModel(BaseModel):
    user = models.OneToOneField(
        "core.UserModel", on_delete=models.CASCADE, related_name="author_profile"
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    profile = models.ImageField(upload_to="authors/", null=True, blank=True)
    revenue_share_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Chapter sale price (MMK) share for this author (0-100).",
    )
    bio = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    social_media = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.name or self.user.username

    def calculate_share(self, sale_price_mmk):
        """Author payout from chapter sale price in MMK (not gem count)."""
        if not self.revenue_share_percent or not sale_price_mmk:
            return 0
        return int(sale_price_mmk * self.revenue_share_percent / 100)

    class Meta:
        app_label = "core"
        db_table = "authors"
        verbose_name = "Author"
        verbose_name_plural = "Authors"


class AuthorSalaryModel(BaseModel):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
    ]

    author = models.ForeignKey(
        AuthorModel,
        on_delete=models.CASCADE,
        related_name="salaries",
    )
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    total_amount_mmk = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True, default="")

    class Meta:
        app_label = "core"
        db_table = "author_salaries"
        verbose_name = "Author Salary"
        verbose_name_plural = "Author Salaries"
        unique_together = ("author", "year", "month")
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.author.display_name} - {self.year}-{self.month:02d}"


class AuthorFollowModel(BaseModel):
    user = models.ForeignKey(
        "core.UserModel",
        on_delete=models.CASCADE,
        related_name="author_follows",
    )
    author = models.ForeignKey(
        AuthorModel,
        on_delete=models.CASCADE,
        related_name="follower_records",
    )

    class Meta:
        app_label = "core"
        db_table = "author_follows"
        verbose_name = "Author Follow"
        verbose_name_plural = "Author Follows"
        unique_together = ("user", "author")

    def __str__(self):
        return f"{self.user.username} follows {self.author.display_name}"
