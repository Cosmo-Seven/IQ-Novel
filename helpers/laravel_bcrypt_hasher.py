# helpers/laravel_bcrypt_hasher.py
#
# Laravel ($2y$) bcrypt hash တွေကို Django ထဲမှာ တိုက်ရိုက် login ဝင်နိုင်အောင်
# custom password hasher ဖြစ်ပါတယ်။
#
# Setup:
#   1. pip install bcrypt
#   2. novel/settings.py ထဲမှာ PASSWORD_HASHERS ထည့်ပါ (အောက်မှာ ဖော်ပြထားသည်)
#
# settings.py ထဲ ဒီ block ထည့်ပါ:
# PASSWORD_HASHERS = [
#     "django.contrib.auth.hashers.PBKDF2PasswordHasher",
#     "helpers.laravel_bcrypt_hasher.LaravelBcryptPasswordHasher",
# ]

from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.crypto import constant_time_compare


class LaravelBcryptPasswordHasher(BasePasswordHasher):
    """
    Laravel/PHP ကနေ export လုပ်ထားတဲ့ $2y$... bcrypt hash တွေကို Django မှာ
    တိုက်ရိုက် verify လုပ်နိုင်တဲ့ hasher ဖြစ်ပါတယ်။

    Stored format:  laravel_bcrypt$$2y$10$<rest of bcrypt hash>
    Migration ပြီးရင် user ရဲ့ password ကို auto-upgrade လုပ်ပေးပါမယ် (PBKDF2 သို့)
    ဒါကြောင့် တဖြေးဖြေး legacy hash တွေ မရှိတော့ပဲ Django native format ဖြစ်သွားပါမယ်။
    """

    algorithm = "laravel_bcrypt"

    def salt(self):
        return ""  # bcrypt က salt ကို hash ထဲမှာ ထည့်ထားပြီးသားပါ

    def encode(self, password, salt):
        raise NotImplementedError("LaravelBcryptPasswordHasher is read-only (import only).")

    @classmethod
    def wrap(cls, laravel_hash: str) -> str:
        """
        Import command ကနေ ခေါ်သုံးပါ:
            stored_password = LaravelBcryptPasswordHasher.wrap("$2y$10$...")
        """
        return f"laravel_bcrypt${laravel_hash}"

    def verify(self, password, encoded):
        try:
            import bcrypt
        except ImportError:
            return False

        # encoded = "laravel_bcrypt$$2y$10$..."
        laravel_hash = encoded[len("laravel_bcrypt$"):]

        # PHP uses $2y$, Python bcrypt uses $2b$ — functionally identical
        compat_hash = laravel_hash.replace("$2y$", "$2b$", 1)

        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                compat_hash.encode("utf-8"),
            )
        except Exception:
            return False

    def safe_summary(self, encoded):
        return {"algorithm": self.algorithm, "hash": encoded[-6:]}

    def must_update(self, encoded):
        # Legacy hash ကို user login ပြီးတာနဲ့ Django native PBKDF2 သို့ auto-upgrade
        return True

    def harden_runtime(self, password, encoded):
        pass
