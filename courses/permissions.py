from rest_framework.permissions import BasePermission, SAFE_METHODS


METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']


class IsAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        # Make sure that user is not Anonymouse
        if request.user.is_authenticated:
            return bool(
                request.user and
                (request.user.is_staff or request.user.role=='TE')
            )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        if request.method in METHODS:
            if request.user.is_authenticated:
                return bool(
                    request.user and
                    (request.user.is_staff or request.user.role=='TE')
                )


class IsAdminOrOwnTeacher(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        if request.user.is_authenticated:    
            if request.method in METHODS:
                return bool(
                    request.user and
                    (request.user.is_staff or obj.user == request.user) 
                )