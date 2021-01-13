from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from . import models
from .models import Profile

#admin.site.register(Profile)

class ProfileInline (admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

#@admin.register(models.User)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances (self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

    fieldsets = UserAdmin.fieldsets
    #fieldsets = UserAdmin.fieldsets + (
    #    (
    #        "Profile",
    #        {
    #            'fields': (
    #                'affiliation',
    #                'position',
    #            )
    #        }
    #    ),
    #)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
