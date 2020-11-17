from django.contrib import admin
from .models import Authority


class AuthorityAdmin(admin.ModelAdmin):
    pass


admin.site.register(Authority, AuthorityAdmin)
