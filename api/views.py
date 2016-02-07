from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from api.permissions import IsSelfOrSuperUser
from rest_framework.permissions import IsAuthenticated
# Serializers define the API representation.


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff', 'first_name', 'last_name')
        partial = True

# ViewSets define the view behavior.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSelfOrSuperUser, )



# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
