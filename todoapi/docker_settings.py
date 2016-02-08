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
    'rest_framework_swagger',
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

SWAGGER_SETTINGS = {
    'is_authenticated': True,
    'permission_denied_handler': 'api.permissions.swagger_permission_denied_handler',
    'info': {
        'contact': 'team-lead@tangentsolutions.co.za',
        'title': 'UserService API',
        'description': """
Welcome to the docs for the UserService

<h2>Authentication</h2>

<p>This API users TOKEN authentication. 
Get the token for an existing user, 
and make sure to add the AUTHORIZATION header to all rquests.
</p>
e.g.:<br/>
<pre><code>curl -X GET http://127.0.0.1:8000/users/ \\
  -H 'Authorization: Token 1234...'
</code></pre>

""",        
    },
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
