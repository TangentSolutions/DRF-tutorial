from django.conf.urls import url, include
from django.contrib import admin
from api.views import router

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # DRF:
    url(r'^', include(router.urls)),
    url(r'^explorer/', 
    	include('rest_framework_swagger.urls', namespace='swagger')),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework'))

]

# Setting up static files for development:
if settings.DEBUG is True:
    urlpatterns = urlpatterns + \
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
