from django.db import migrations, models


def copy_user_to_users(apps, schema_editor):
    RewardModel = apps.get_model("core", "RewardModel")
    for reward in RewardModel.objects.exclude(user__isnull=True).iterator():
        reward.users.add(reward.user_id)


def copy_users_to_user(apps, schema_editor):
    RewardModel = apps.get_model("core", "RewardModel")
    for reward in RewardModel.objects.iterator():
        first_id = reward.users.values_list("id", flat=True).first()
        if first_id:
            reward.user_id = first_id
            reward.save(update_fields=["user"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_alter_rewardmodel_amount_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="rewardmodel",
            name="users",
            field=models.ManyToManyField(
                blank=True,
                help_text="ချန်ထားရင် user အားလုံးအတွက်",
                related_name="rewards",
                to="core.usermodel",
            ),
        ),
        migrations.RunPython(copy_user_to_users, copy_users_to_user),
        migrations.RemoveField(
            model_name="rewardmodel",
            name="user",
        ),
    ]
