from rest_framework import permissions


class IsDriver(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):

        # permissions are only allowed to the owner of the snippet.
        return obj.driver == request.user


class IsCreationOrIsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            if view.action == 'create':
                return True
            else:
                return False
        else:
            if request.method in permissions.SAFE_METHODS:
                return True


class IsGetOrIsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            if request.method == 'GET':
                return True
            else:
                return False
        else:
            if request.method in permissions.SAFE_METHODS:
                return True