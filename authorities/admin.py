from django.contrib import admin
from .models import (
    Authority,
    FOIRequest,
)


class AuthorityAdmin(admin.ModelAdmin):
    pass
admin.site.register(Authority, AuthorityAdmin)


class FOIRequestAdmin(admin.ModelAdmin):
    pass
admin.site.register(FOIRequest, FOIRequestAdmin)
