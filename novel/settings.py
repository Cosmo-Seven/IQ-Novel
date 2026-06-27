from pathlib import Path
import environ
import os

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

DOMAIN = env("DOMAIN", default="")
MAINTENANCE_MODE = True
COMING_SOON = True
HYPER = env("HYPER")
SITE_ID = 1
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

DASHBOARD_LOGIN_URL = env("DASHBOARD_LOGIN_URL")
DASHBOARD_LOGOUT_URL = env("DASHBOARD_LOGOUT_URL")
ADMIN_LOGIN_URL = env("ADMIN_LOGIN_URL")
LOGIN_URL = env("LOGIN_URL")
PROJECT_NAME = env("PROJECT_NAME", default="")

AUTH_USER_MODEL = "core.UserModel"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "pwa",
    "ckeditor",
    "core",
    "django.contrib.sites",
]

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "middlewares.internal_server_error.InternalServerErrorMiddleware",
]

ROOT_URLCONF = f"{PROJECT_NAME}.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "utils.site.site",
                "utils.routes.routes",
                "utils.languages.languages",
                "utils.sidebar.sidebar",
            ],
        },
    },
]

REDIS_URL = env("REDIS_URL", default="redis://127.0.0.1:6379")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

WSGI_APPLICATION = f"{PROJECT_NAME}.wsgi.application"
ASGI_APPLICATION = f"{PROJECT_NAME}.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE"),
        "NAME": (
            BASE_DIR / env("DB_NAME")
            if env("DB_ENGINE") == "django.db.backends.sqlite3"
            else env("DB_NAME")
        ),
        "USER": env("DB_USER", default=""),
        "PASSWORD": env("DB_PASSWORD", default=""),
        "HOST": env("DB_HOST", default=""),
        "PORT": env("DB_PORT", default=""),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = env("LANGUAGE_CODE", default="en-us")
TIME_ZONE = env("TIME_ZONE", default="Asia/Yangon")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]


MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


PWA_APP_NAME = "novel"
PWA_APP_DESCRIPTION = ""
PWA_APP_THEME_COLOR = "#f7f7f7"
PWA_APP_BACKGROUND_COLOR = "#ffabab"
PWA_APP_DISPLAY = "standalone"

PWA_APP_SCOPE = "/"
PWA_APP_START_URL = "/"
PWA_APP_ORIENTATION = "portrait"
PWA_APP_STATUS_BAR_COLOR = "default"
PWA_SERVICE_WORKER_PATH = BASE_DIR / "templates" / "pwa" / "serviceworker.js"
PWA_APP_DIR = "ltr"
PWA_APP_LANG = "en-US"
PWA_APP_ICONS = [
    {
        "src": "/static/website/images/logo.png",
        "sizes": "192x192",
        "purpose": "any maskable",
    },
    {"src": "/static/website/images/logo.png", "sizes": "512x512", "purpose": "any"},
]
# CKEditor Configuration - Simple text formatting only
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Basic',
        'height': 300,
        'toolbar_Basic': [
            ['Bold', 'Italic', 'Underline', 'Strike'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'], # ဒီကောင်တွေ အလုပ်လုပ်ဖို့က justify plugin လိုပါတယ်
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            ['RemoveFormat']
        ],
        'removePlugins': 'elementspath,resize',
        'extraPlugins': 'justify',
        'allowedContent': True,
        'extraAllowedContent': 'p;span;ul;li;ol;a;strong;em;u;s;div{text-align};*[align]',
        'basicEntities': False,
        'entities': False,
    },
}

VAPID_PRIVATE_KEY = "jO2MllsWdvza5_wsx1FtLUFLSI7u1P_uy-gvIe7jQYs"
VAPID_PUBLIC_KEY  = "BG8PMB1Bcc1WF5rwYzga--TpVNijZylmfsA1f0lqpC2FgV4ju4I_Cp2QD6WR7oMedT-kI2zrIc4YJ-Nn2P_Duwk"
VAPID_ADMIN_EMAIL = "mailto:admin@novelphilia.com"