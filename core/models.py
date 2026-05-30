from django.db import models
from models.language_models import LanguageModel
from models.role_models import RoleModel
from models.site_models import SiteModel
from models.text_key_models import TextKeyModel
from models.translation_models import TranslationModel
from models.user_models import UserModel


# // Project Model ------------------------------------------------------
from models.novel_models import GenreModel, NovelModel, NovelChapterModel, BookmarkModel, ChapterPurchaseModel
from models.payment_method_models import PaymentMethodModel
from models.slider_models import SliderModel
from models.gem_models import GemModel, GemOrderModel