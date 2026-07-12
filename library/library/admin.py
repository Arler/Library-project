from django.contrib import admin
from django.shortcuts import redirect


class CustomAdminSite(admin.AdminSite):

    def admin_view(self, *args, **kwargs):
        original_view = super().admin_view(*args, **kwargs)

        def wrapper(request, *args, **kwargs):
            if not request.user.is_staff:
                return redirect('/')
            else:
                return original_view(request, *args, **kwargs)
            
        return wrapper