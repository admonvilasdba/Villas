from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Category, Dish, SubCategory


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1
    fields = ('name', 'order', 'is_active')
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'order', 'is_active', 'subcategory_count', 'dish_count')
    list_editable = ('order', 'is_active')
    search_fields = ('name',)
    inlines = (SubCategoryInline,)

    @admin.display(description='subcategorías')
    def subcategory_count(self, obj):
        return obj.subcategories.count()

    @admin.display(description='platillos')
    def dish_count(self, obj):
        return Dish.objects.filter(subcategory__category=obj).count()


@admin.register(SubCategory)
class SubCategoryAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'category', 'order', 'is_active', 'dish_count')
    list_filter = ('is_active', 'category')
    list_editable = ('order', 'is_active')
    search_fields = ('name',)
    autocomplete_fields = ('category',)

    @admin.display(description='platillos')
    def dish_count(self, obj):
        return obj.dishes.count()


@admin.register(Dish)
class DishAdmin(TabbedTranslationAdmin):
    list_display = (
        'image_preview',
        'name',
        'subcategory',
        'price',
        'prep_time_minutes',
        'is_available',
        'order',
    )
    list_filter = ('is_available', 'subcategory__category', 'subcategory')
    list_editable = ('price', 'prep_time_minutes', 'is_available', 'order')
    search_fields = ('name', 'description')
    autocomplete_fields = ('subcategory',)
    readonly_fields = ('image_preview',)
    actions = ('mark_available', 'mark_unavailable')
    fieldsets = (
        (None, {
            'fields': ('subcategory', 'name', 'description'),
        }),
        ('Detalles', {
            'fields': ('price', 'prep_time_minutes', 'image', 'image_preview', 'is_available', 'order'),
        }),
    )

    @admin.display(description='imagen')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:6px;" />',
                obj.image.url,
            )
        return '—'

    @admin.action(description='Marcar como disponibles')
    def mark_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} platillo(s) marcado(s) como disponibles.')

    @admin.action(description='Marcar como agotados')
    def mark_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} platillo(s) marcado(s) como agotados.')
