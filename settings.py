# -*- coding: utf-8 -*-
from getenv import env

INSTALLED_ADDONS = [
    # <INSTALLED_ADDONS>  # Warning: text inside the INSTALLED_ADDONS tags is auto-generated. Manual changes will be overwritten.
    'aldryn-addons',
    'aldryn-django',
    'aldryn-django-cms',
    'djangocms-bootstrap4',
    'djangocms-picture',
    'djangocms-style',
    'djangocms-text-ckeditor',
    'djangocms-transfer',
    'django-filer',
    # </INSTALLED_ADDONS>
]

import aldryn_addons.settings
aldryn_addons.settings.load(locals())

USE_TZ = True
TIME_ZONE = 'America/New_York'

CMS_TEMPLATES = (
    ('home.html', 'Home'),
    ('category.html', 'Category'),
)
CMS_LANGUAGES = {
    'default': {
        'fallbacks': ['es', 'en'],
        'redirect_on_fallback': False,
        'public': True,
        'hide_untranslated': True,
    },
    1: [
        {'code': 'es', 'name': 'Spanish', 'fallbacks': [], 'public': True},
        {'code': 'en', 'name': 'English', 'fallbacks': [], 'public': True},
    ]
}
CMS_PAGE_CACHE = True

# all django settings can be altered here
ENABLE_SYNCING = False
STATIC_ROOT = '/static'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
INSTALLED_APPS.extend([
    # Third party
    'account',
    'core',
])

MIDDLEWARE.insert(
    MIDDLEWARE.index('django.middleware.locale.LocaleMiddleware') + 1,
    'cms_extensions.middleware.LanguageCookieMiddleware',
)
MIDDLEWARE.remove('cms.middleware.language.LanguageCookieMiddleware')

# Captcha
if env('RECAPTCHA_PUBLIC_KEY') and env('RECAPTCHA_PRIVATE_KEY'):
    RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY')
else:
    # Use the test keys and be quiet about it
    SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

# Accounts
LOGIN_URL = 'account_login'
ACCOUNT_LANGUAGES = (('es', 'Spanish'), ('en', 'English'))
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_LOGIN_REDIRECT_URL = 'account_dashboard'
ACCOUNT_SETTINGS_REDIRECT_URL = 'account_dashboard'
ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL = 'account_dashboard'
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True
ACCOUNT_EMAIL_CONFIRMATION_AUTO_LOGIN = False
ACCOUNT_USER_DISPLAY = lambda user: user.email
AUTHENTICATION_BACKENDS.append('account.auth_backends.EmailAuthenticationBackend')


def ACCOUNT_DELETION_MARK_CALLBACK(account_deletion):
    # Fixes https://github.com/pinax/django-user-accounts/issues/241
    from account.hooks import hookset
    hookset.account_delete_expunge(account_deletion)


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'