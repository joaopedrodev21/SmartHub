from rest_framework import permissions

class IsCompanyOwner(permissions.BasePermission):
    """Permite o acesso apenas ao proprietário da empresa."""
    message = 'Você não tem permissão para acessar este recurso.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        company = user.companies.first()
        return bool(company and company.owner == user)