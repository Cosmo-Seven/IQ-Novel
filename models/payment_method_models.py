from django.db import models
from models.base_models import BaseModel
from django.utils.text import slugify
from helpers.translation import register_key


class PaymentMethodModel(BaseModel):
    account_name = models.CharField(max_length=200)
    holder_name = models.CharField(max_length=200, null=True, blank=True)
    logo = models.ImageField(upload_to="payment_method", null=True, blank=True)
    account_number = models.CharField(max_length=200, null=True, blank=True)
    account_phone = models.CharField(max_length=20, null=True, blank=True)


    class Meta:
        app_label = "core"
        db_table = "payment_methods"
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"

    def __str__(self):
        return f"{self.account_name} - {self.account_name}"

    def save(self, *args, **kwargs):
        key = slugify(self.account_name).replace("-", "_").lower()
        register_key(key, self.account_name)
        super().save(*args, **kwargs)

    @property
    def translation_key(self):
        return slugify(self.account_name).replace("-", "_").lower()