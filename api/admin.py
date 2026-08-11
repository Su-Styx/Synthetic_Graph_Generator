from django.contrib import admin

# Register your models here.
from .models import Run, GenModel

admin.site.register(Run)



@admin.register(GenModel)
class GenModelAdmin(admin.ModelAdmin):
    list_display = ("type", "efficiency", "id")
    list_filter = ("efficiency",)
    search_fields = ("type", "parameters", "documentation", "paper")