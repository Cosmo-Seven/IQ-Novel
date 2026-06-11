from django.db import models
from models.language_models import LanguageModel
from models.role_models import RoleModel
from models.site_models import SiteModel
from models.text_key_models import TextKeyModel
from models.translation_models import TranslationModel
from models.user_models import UserModel


# // Project Model ------------------------------------------------------
from models.genre_models import GenreModel
from models.novel_models import NovelModel
from models.bookmark_models import BookmarkModel
from models.download_models import DownloadModel
from models.chapter_models import ChapterModel, ChapterPurchaseModel, ChapterReadModel
from models.payment_method_models import PaymentMethodModel
from models.slider_models import SliderModel
from models.gem_models import GemModel, GemOrderModel
from models.author_models import AuthorModel, AuthorSalaryModel, AuthorFollowModel
from models.comment_models import CommentModel
from models.novel_view_models import NovelViewModel
from models.reward_models import RewardModel, DailyRewardModel