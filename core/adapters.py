from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class SocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get("email")

        if not email:
            emails = sociallogin.account.extra_data.get("emails", [])
            if emails:
                email = emails[0].get("email")

        if email:
            try:
                user = User.objects.get(email=email)

                if not sociallogin.is_existing:
                    sociallogin.connect(request, user)

            except User.DoesNotExist:
                pass
