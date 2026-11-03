from django.db.models import Prefetch
from django.views.generic import ListView, TemplateView

from .models import Category, Dish, SubCategory


class MenuView(ListView):
    template_name = 'menu/index.html'
    context_object_name = 'categories'

    def get_queryset(self):
        available_dishes = Dish.objects.filter(is_available=True).order_by('order', 'name')
        active_subcategories = (
            SubCategory.objects.filter(is_active=True)
            .order_by('order', 'name')
            .prefetch_related(Prefetch('dishes', queryset=available_dishes))
        )
        return (
            Category.objects.filter(is_active=True)
            .order_by('order', 'name')
            .prefetch_related(Prefetch('subcategories', queryset=active_subcategories))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        visible = []
        for category in context['categories']:
            subcategories = []
            for subcategory in category.subcategories.all():
                dishes = list(subcategory.dishes.all())
                if not dishes:
                    continue
                subcategory.has_dish_images = any(dish.image for dish in dishes)
                subcategories.append(subcategory)
            if subcategories:
                category.visible_subcategories = subcategories
                visible.append(category)
        context['categories'] = visible
        return context


class AboutView(TemplateView):
    template_name = 'menu/about.html'
