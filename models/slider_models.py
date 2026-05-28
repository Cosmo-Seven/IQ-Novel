from django.db import models
from models.base_models import BaseModel


class SliderModel(BaseModel):
    image = models.ImageField(upload_to="slider")
    status = models.BooleanField(default=True)

    class Meta:
        app_label = "core"
        db_table = "sliders"
        verbose_name = "Slider"
        verbose_name_plural = "Sliders"
