# Generated: switch Review Campaign from single-winner to multi-winner

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_reviewcampaign_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reviewcampaignmodel',
            name='winner_review',
        ),
        migrations.RemoveField(
            model_name='reviewcampaignmodel',
            name='is_awarded',
        ),
        migrations.RemoveField(
            model_name='reviewcampaignmodel',
            name='awarded_at',
        ),
        migrations.RemoveField(
            model_name='reviewcampaignmodel',
            name='awarded_by',
        ),
        migrations.AddField(
            model_name='campaignreviewmodel',
            name='is_winner',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='campaignreviewmodel',
            name='awarded_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='reviewcampaignmodel',
            name='reward_amount',
            field=models.PositiveIntegerField(default=0, help_text='Winner တစ်ယောက်စီကို ပေးမယ့် diamond (gem) အရေအတွက်'),
        ),
    ]
