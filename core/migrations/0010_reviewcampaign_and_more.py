# Generated for Review Campaign feature

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_chaptermodel_delete_approved_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewCampaignModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, default='')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('reward_amount', models.PositiveIntegerField(default=0, help_text='Winner ကို ပေးမယ့် diamond (gem) အရေအတွက်')),
                ('is_awarded', models.BooleanField(default=False)),
                ('awarded_at', models.DateTimeField(blank=True, null=True)),
                ('awarded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Review Campaign',
                'verbose_name_plural': 'Review Campaigns',
                'db_table': 'review_campaigns',
            },
        ),
        migrations.CreateModel(
            name='CampaignReviewModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('image', models.ImageField(upload_to='campaign_reviews')),
                ('content', models.TextField()),
                ('is_approved', models.BooleanField(default=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='core.reviewcampaignmodel')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('novel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaign_reviews', to='core.novelmodel')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaign_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Campaign Review',
                'verbose_name_plural': 'Campaign Reviews',
                'db_table': 'campaign_reviews',
            },
        ),
        migrations.AddField(
            model_name='reviewcampaignmodel',
            name='winner_review',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='won_campaign', to='core.campaignreviewmodel'),
        ),
        migrations.CreateModel(
            name='CampaignReviewLikeModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='core.campaignreviewmodel')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaign_review_likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Campaign Review Like',
                'verbose_name_plural': 'Campaign Review Likes',
                'db_table': 'campaign_review_likes',
                'unique_together': {('review', 'user')},
            },
        ),
    ]
