from django.db import models

# ---------- SeriesModel ---------- #
class StatusEnum(models.TextChoices):
    ONGOING = "ongoing", "Ongoing"
    COMPLETE = "complete", "Complete"