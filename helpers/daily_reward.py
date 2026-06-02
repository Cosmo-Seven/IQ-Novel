from django.utils import timezone
from django.db import models
from datetime import date
from core.models import RewardModel, DailyRewardModel, UserModel


def process_daily_reward(user):
    """
    Process daily rewards for a user on login.
    Returns the total amount awarded today, or 0 if no rewards are applicable.
    """
    today = date.today()
    current_datetime = timezone.now()
    total_awarded = 0

    # Get all applicable rewards for this user
    # Rewards can be:
    # 1. Specific to this user (user_id matches)
    # 2. Global rewards (user_id is NULL)
    applicable_rewards = RewardModel.objects.filter(
        start_date__date__lte=today,
        end_date__date__gte=today,
    ).filter(
        models.Q(user__isnull=True) | models.Q(user=user)
    )

    for reward in applicable_rewards:
        # Check if this reward was already claimed today by this user
        already_claimed = DailyRewardModel.objects.filter(
            reward=reward,
            user=user,
            claim_date=today,
        ).exists()

        if not already_claimed:
            # Award the gem/amount
            user.gem = (user.gem or 0) + reward.amount
            user.save(update_fields=["gem"])

            # Record the claim
            DailyRewardModel.objects.create(
                reward=reward,
                user=user,
                amount_received=reward.amount,
            )

            total_awarded += reward.amount

    return total_awarded
