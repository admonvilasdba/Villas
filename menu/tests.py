from decimal import Decimal

from django.contrib import admin
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from .models import Category, Dish, SubCategory


class ModelTests(TestCase):
    def test_category_slug_is_generated(self):
        category = Category.objects.create(name='Entradas')
        self.assertEqual(category.slug, 'entradas')

    def test_subcategory_str_includes_category(self):
        category = Category.objects.create(name='Bebidas')
        subcategory = SubCategory.objects.create(category=category, name='Cafés')
        self.assertEqual(str(subcategory), 'Bebidas · Cafés')

    def test_dish_price_and_prep_time_display(self):
        category = Category.objects.create(name='Postres')
        subcategory = SubCategory.objects.create(category=category, name='Dulces')
        dish = Dish.objects.create(
            subcategory=subcategory,
            name='Pastel',
            price=Decimal('12.50'),
            prep_time_minutes=15,
        )
        self.assertEqual(dish.price, Decimal('12.50'))
        self.assertEqual(dish.prep_time_display, '15 min')

    def test_dish_prep_time_display_empty_when_not_set(self):
        category = Category.objects.create(name='Postres')
        subcategory = SubCategory.objects.create(category=category, name='Dulces')
        dish = Dish.objects.create(subcategory=subcategory, name='Flan', price=Decimal('8'))
        self.assertEqual(dish.prep_time_display, '')

    def test_str_returns_name(self):
        category = Category.objects.create(name='Carnes')
        self.assertEqual(str(category), 'Carnes')


class MenuViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Principales', order=1)
        self.subcategory = SubCategory.objects.create(
            category=self.category, name='Carnes', order=1
        )
        self.available = Dish.objects.create(
            subcategory=self.subcategory,
            name='Bistec',
            price=Decimal('20.00'),
            is_available=True,
        )
        self.sold_out = Dish.objects.create(
            subcategory=self.subcategory,
            name='Pollo agotado',
            price=Decimal('15.00'),
            is_available=False,
        )

    def test_menu_url_uses_spanish_prefix_by_default(self):
        with translation.override('es'):
            self.assertEqual(reverse('menu:index'), '/es/')

    def test_menu_url_uses_english_prefix(self):
        with translation.override('en'):
            self.assertEqual(reverse('menu:index'), '/en/')

    def test_menu_shows_only_available_dishes(self):
        response = self.client.get(reverse('menu:index'))
        self.assertEqual(response.status_code, 200)
        dishes = response.context['categories'][0].visible_subcategories[0].dishes.all()
        self.assertIn(self.available, dishes)
        self.assertNotIn(self.sold_out, dishes)

    def test_inactive_category_is_hidden(self):
        inactive = Category.objects.create(name='Oculta', is_active=False)
        SubCategory.objects.create(category=inactive, name='Sub')
        response = self.client.get(reverse('menu:index'))
        names = [c.name for c in response.context['categories']]
        self.assertNotIn('Oculta', names)

    def test_category_without_available_dishes_is_hidden(self):
        empty = Category.objects.create(name='Sin platillos', is_active=True)
        SubCategory.objects.create(category=empty, name='Vacía')
        response = self.client.get(reverse('menu:index'))
        names = [c.name for c in response.context['categories']]
        self.assertNotIn('Sin platillos', names)

    def test_menu_english_prefix(self):
        response = self.client.get('/en/')
        self.assertEqual(response.status_code, 200)

    def test_spanish_ui_is_default(self):
        response = self.client.get('/es/')
        self.assertContains(response, 'Nuestra Carta')

    def test_english_ui_translation(self):
        response = self.client.get('/en/')
        self.assertContains(response, 'Our Menu')


class AdminRegistrationTests(TestCase):
    def test_models_registered_in_admin(self):
        self.assertTrue(admin.site.is_registered(Category))
        self.assertTrue(admin.site.is_registered(SubCategory))
        self.assertTrue(admin.site.is_registered(Dish))
