from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAcademyOwnerOrReadOnly(BasePermission):
    """Solo el dueño de la academia puede modificar."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated


    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsCourseAcademyOwnerOrReadOnly(BasePermission):
    """
    - GET / HEAD / OPTIONS: público.
    - POST / PUT / PATCH / DELETE: solo usuario autenticado y dueño de la academia del curso.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.academy.owner == request.user


class IsTeacherAcademyOwnerOrReadOnly(BasePermission):
    """Solo el dueño de la academia del profesor puede modificar."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.academy.owner == request.user


class IsConvocatoriaCourseOwnerOrReadOnly(BasePermission):
    """Solo el dueño de la academia del curso de la convocatoria puede modificar."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.course.academy.owner == request.user


class IsStudentOwnerOrReadOnly(BasePermission):
    """Solo el alumno dueño del recurso puede modificar."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.student == request.user


class IsStaffOrReadOnly(BasePermission):
    """Solo staff escribe. Cualquiera lee."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_staff
