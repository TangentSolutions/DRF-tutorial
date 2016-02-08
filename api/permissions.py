from rest_framework import permissions
from django.http import HttpResponseRedirect 

class IsSelfOrSuperUser(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_permission(self, request, view):

        user_not_logged_in = not request.user.is_authenticated()
        if user_not_logged_in:
            return False

        if request.user.is_superuser:
            return True

        # only normal users from here down:
        if view.action in ['create', 'delete']:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        
        # Instance must have an attribute named `owner`.
        if request.user.is_superuser:
        	return True
        
        return obj.pk == request.user.pk


def swagger_permission_denied_handler(request):

    redirect_url = "/api-auth/login/?next=/explorer/"
    return HttpResponseRedirect(redirect_url)
