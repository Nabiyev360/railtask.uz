from django.contrib import admin

from .models import Profile, Department



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
    search_fields = ('full_name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name',)
