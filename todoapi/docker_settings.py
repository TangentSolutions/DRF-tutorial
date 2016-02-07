"""
NB: All custom configuration for the project be done here
Never edit settings.py directly
"""

from django.conf import settings
import os

# connect to the linked docker postgres db
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

# we extend INSTALLED_APPS here.
# Any apps you want to install you can
# just add here (or use app.py)
settings.INSTALLED_APPS.extend([
    'rest_framework',
    'api',
])

# Rest framework settings
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions'
    ]
}

# We set the static root to the mapped volume /code
# When you run docker-compose run web python manage.py collectstatic
# You will notice that it creates a `static` directory in the
# root folder of the project
STATIC_ROOT = '/code/static/'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--with-spec', '--spec-color',
             '--with-coverage', '--cover-html',
             '--cover-package=.', '--cover-html-dir=reports/cover']
