from django.contrib import admin

from .models import Category, Convocatoria, Course, CourseImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "academy", "category", "status", "created_at"]
    list_filter = ["status", "level", "modality"]
    search_fields = ["title", "description", "academy__name"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Convocatoria)
class ConvocatoriaAdmin(admin.ModelAdmin):
    list_display = ["course", "start_date", "price", "total_places", "is_active"]
    list_filter = ["is_active", "modality"]
    search_fields = ["course__title"]


@admin.register(CourseImage)
class CourseImageAdmin(admin.ModelAdmin):
    list_display = ["course", "is_primary", "position"]
    list_filter = ["is_primary"]