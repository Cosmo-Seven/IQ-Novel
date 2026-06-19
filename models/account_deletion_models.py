import uuid
from django.db import models
from django.utils.timezone import now
from models.base_models import BaseModel
from django.utils.translation import gettext_lazy as _


class AccountDeletionRequestModel(BaseModel):
    """Model for user account deletion requests"""
    
    class StatusChoices(models.TextChoices):
        PENDING = "pending", _("Pending")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")
    
    user = models.ForeignKey(
        "core.UserModel", 
        on_delete=models.CASCADE,
        related_name="deletion_requests",
        verbose_name=_("User")
    )
    
    reason = models.TextField(
        verbose_name=_("Reason for deletion"),
        null=True,
        blank=True
    )
    
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        verbose_name=_("Status")
    )
    
    approved_by = models.ForeignKey(
        "core.UserModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_deletions",
        verbose_name=_("Approved By")
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Approved At")
    )
    
    class Meta:
        app_label = "core"
        db_table = "account_deletion_requests"
        verbose_name = _("Account Deletion Request")
        verbose_name_plural = _("Account Deletion Requests")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.status}"
    
    def approve(self, admin_user):
        """Approve the deletion request"""
        self.status = self.StatusChoices.APPROVED
        self.approved_by = admin_user
        self.approved_at = now()
        self.save()
        
        # Soft delete the user account
        self.user.is_active = False
        self.user.soft_delete()
        self.user.save()
    
    def reject(self, admin_user):
        """Reject the deletion request"""
        self.status = self.StatusChoices.REJECTED
        self.approved_by = admin_user
        self.approved_at = now()
        self.save()
    
    def is_pending(self):
        return self.status == self.StatusChoices.PENDING
    
    def is_approved(self):
        return self.status == self.StatusChoices.APPROVED
    
    def is_rejected(self):
        return self.status == self.StatusChoices.REJECTED