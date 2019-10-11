from rest_framework import permissions


class PermissionMapper(permissions.AllowAny):
    message = ""

    def has_permission(self, request, view):
        for klass, actions in getattr(view, 'has_permissions', {}).items():
            if view.action in actions:
                if hasattr(klass(), 'message'):
                    self.message = klass().message
                return klass().has_permission(request, view)
        return True

    def has_object_permission(self, request, view, obj):
        for klass, actions in getattr(view, 'has_object_permissions', {}).items():
            if view.action in actions:
                if hasattr(klass(), 'message'):
                    self.message = klass().message
                return klass().has_object_permission(request, view, obj)
        return True


class AnonPermissionOnly(permissions.BasePermission):
    message = 'You are already authenticated. Please log out.'

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsUserOwner(permissions.BasePermission):

    message = 'You are not the owner of this user profile.'

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsPostOwner(permissions.BasePermission):

    message = 'You are not the owner of this post.'

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
