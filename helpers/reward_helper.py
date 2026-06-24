# helpers/reward_helper.py

from django.utils import timezone
from core.models import RewardModel


def get_active_chapter_reward(user=None):
    """
    free_read သို့မဟုတ် discount_read reward တစ်ခု active ဖြစ်နေလား စစ်
    user specific ရှိရင် သူ့ကို ဦးစားပေး၊ မရှိရင် global (user=None) ကြည့်
    """
    now = timezone.now()

    base_qs = RewardModel.objects.filter(
        start_date__lte=now,
        end_date__gte=now,
        reward_type__in=[
            RewardModel.RewardType.FREE_READ,
            RewardModel.RewardType.DISCOUNT_READ,
        ],
    )

    # user specific reward ဦးစားပေး
    if user and user.is_authenticated:
        reward = base_qs.filter(user=user).first()
        if reward:
            return reward

    # global reward (user=None)
    return base_qs.filter(user=None).first()


def get_effective_price(chapter, user=None):
    """
    Chapter ရဲ့ actual price ကို reward စစ်ပြီး return
    return: (effective_price, reward_type or None)
    """
    if chapter.is_free:
        return 0, None

    reward = get_active_chapter_reward(user)

    if reward is None:
        return chapter.gem_price, None

    if reward.reward_type == RewardModel.RewardType.FREE_READ:
        return 0, reward.reward_type

    if reward.reward_type == RewardModel.RewardType.DISCOUNT_READ:
        return 1, reward.reward_type

    return chapter.gem_price, None