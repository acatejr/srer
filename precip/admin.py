from django.contrib import admin
from .models import PrecipEvent, Raingage

admin.site.site_header = 'SRER'
admin.site.index_title = 'Modules'
admin.site.site_title = 'SRER Precip Adminsitration'

class PrecipEventInline(admin.TabularInline):
    model = PrecipEvent

@admin.register(Raingage)
class RaingageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'created', 'updated']
    inlines = [PrecipEventInline]

@admin.register(PrecipEvent)
class PrecipEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'raingage', 'year', 'month', 'precip']
    list_per_page = 15
