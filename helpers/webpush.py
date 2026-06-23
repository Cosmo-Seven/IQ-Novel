# helpers/webpush.py

import json
import logging
from pywebpush import webpush, WebPushException
from django.conf import settings

logger = logging.getLogger(__name__)


def send_push_notification(subscription, title: str, body: str, url: str = "/"):
    """
    subscription = NovelPushSubscriptionModel instance
    """
    payload = json.dumps({
        "title": title,
        "body":  body,
        "url":   url,
    })

    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh_key,
                    "auth":   subscription.auth_key,
                },
            },
            data=payload,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_ADMIN_EMAIL},
        )
    except WebPushException as e:
        if e.response and e.response.status_code == 410:
            logger.info("Subscription expired, removing: %s", subscription.endpoint)
            subscription.delete()
        else:
            logger.error("WebPush failed: %s", e)


def notify_novel_subscribers(novel, title: str, body: str, url: str = "/"):
    from core.models import NovelPushSubscriptionModel

    subscriptions = NovelPushSubscriptionModel.objects.filter(novel=novel)
    for sub in subscriptions:
        send_push_notification(sub, title, body, url)