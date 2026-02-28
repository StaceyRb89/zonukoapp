"""
Django settings for Zonuko project.
"""
from pathlib import Path
import os
import dj_database_url
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
# Try .env.local first (for development), then fall back to .env
env_file = BASE_DIR / ".env.local"
if not env_file.exists():
    env_file = BASE_DIR / ".env"
load_dotenv(env_file)


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-change-me")
DEBUG = env_bool("DJANGO_DEBUG", True)

# Launch mode: "FOUNDING" (pre-launch, collect 200 signups) or "PUBLIC" (open to all)
LAUNCH_MODE = os.environ.get("LAUNCH_MODE", "FOUNDING")  # Change to "PUBLIC" after 200 signups

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split() or [
    "localhost", 
    "127.0.0.1",
    "178.62.107.167",
    "zonuko.co.uk",
    "www.zonuko.co.uk",
]

CSRF_TRUSTED_ORIGINS = [
    "https://zonuko.co.uk",
    "https://www.zonuko.co.uk",
]

INSTALLED_APPS = [
    "jazzmin",  # Must be before django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third party apps
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "storages",
    "tinymce",
    "allauth.socialaccount.providers.google",
    # Local apps
    "apps.core",
    "apps.founding",
    "apps.users",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "zonuko.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "zonuko.context_processors.launch_mode",  # Make LAUNCH_MODE available in all templates
            ],
        },
    },
]

WSGI_APPLICATION = "zonuko.wsgi.application"

# Database configuration

# Use SQLite for local development if no DATABASE_URL is set
if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            default=os.environ.get("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django sites framework
SITE_ID = 1

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Django-allauth settings
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
LOGIN_REDIRECT_URL = "/members/dashboard/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

# Development override: allow login without email verification
if DEBUG:
    ACCOUNT_EMAIL_VERIFICATION = "none"
    ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False

# Email settings
if os.environ.get("EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("EMAIL_HOST")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
    EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
else:
    # Development - console backend
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Zonuko Team <support@zonuko.co.uk>")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "support@zonuko.co.uk")
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Zonuko] "

# Stripe settings
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Digital Ocean Spaces Configuration
AWS_ACCESS_KEY_ID = os.environ.get("SPACES_ACCESS_KEY", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("SPACES_SECRET_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.environ.get("SPACES_BUCKET_NAME", "zonuko-media")
AWS_S3_ENDPOINT_URL = os.environ.get("SPACES_ENDPOINT", "https://nyc3.digitaloceanspaces.com")
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_LOCATION = "media"
AWS_DEFAULT_ACL = "public-read"
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.nyc3.digitaloceanspaces.com"

# Use Digital Ocean Spaces for media storage in production
if not DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "zonuko.storage_backends.MediaStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"
else:
    # Development - use local filesystem
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

# Jazzmin Admin Theme Configuration
JAZZMIN_SETTINGS = {
    "site_title": "Zonuko Admin",
    "site_header": "Zonuko",
    "site_brand": "🚀 Zonuko Learning",
    "welcome_sign": "Welcome to Zonuko Content Manager",
    "copyright": "Zonuko Learning Adventures",
    "search_model": ["users.Project", "users.ChildProfile"],
    
    # Top Menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Site", "url": "/", "new_window": True},
        {"name": "Projects", "url": "admin:users_project_changelist", "permissions": ["users.view_project"]},
    ],
    
    # User Menu
    "usermenu_links": [
        {"model": "auth.user"}
    ],
    
    # Side Menu
    "show_sidebar": True,
    "navigation_expanded": True,
    
    # UI Tweaks - Your Purple Gradient!
    "custom_css": "css/admin_custom.css",
    "custom_js": "js/admin_enhancements.js",
    
    # Icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "users.ParentProfile": "fas fa-user-circle",
        "users.ChildProfile": "fas fa-child",
        "users.Project": "fas fa-rocket",
        "users.ProjectProgress": "fas fa-tasks",
        "users.Subscription": "fas fa-credit-card",
    },
    
    # Color scheme
    "theme": "flatly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-purple",
    "accent": "accent-primary",
    "navbar": "navbar-purple navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-purple",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "flatly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

# TinyMCE Configuration
TINYMCE_DEFAULT_CONFIG = {
    "height": 400,
    "width": "100%",
    "menubar": False,
    "plugins": "link lists emoticons code preview fullscreen",
    "toolbar": "undo redo | formatselect | bold italic underline | forecolor backcolor | alignleft aligncenter alignright | bullist numlist | link emoticons | code preview fullscreen",
    "toolbar_mode": "sliding",
    "content_style": "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 16px; }",
    "elementpath": False,
    "branding": False,
    "promotion": False,
}

