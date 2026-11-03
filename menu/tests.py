import os
from decimal import Decimal
from unittest import mock

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from .models import Category, Dish, SubCategory
from .storage import SupabaseS3Storage


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

    def test_mixed_subcategory_reserves_media_with_placeholder(self):
        self.available.image = 'https://example.com/bistec.jpg'
        self.available.save(update_fields=['image'])
        Dish.objects.create(
            subcategory=self.subcategory,
            name='Sin foto',
            price=Decimal('10.00'),
            is_available=True,
        )

        response = self.client.get(reverse('menu:index'))

        self.assertContains(response, 'class="dish__media is-loading"')
        self.assertContains(response, 'dish__media--placeholder')

    def test_subcategory_without_images_keeps_cards_compact(self):
        response = self.client.get(reverse('menu:index'))
        self.assertNotContains(response, 'class="dish__media')

    def test_image_space_is_decided_per_subcategory(self):
        self.available.image = 'https://example.com/bistec.jpg'
        self.available.save(update_fields=['image'])
        pizzas = SubCategory.objects.create(
            category=self.category, name='Pizzas', order=2
        )
        Dish.objects.create(
            subcategory=pizzas,
            name='Pizza',
            price=Decimal('18.00'),
            is_available=True,
        )

        response = self.client.get(reverse('menu:index'))

        subcategories = {
            subcategory.name: subcategory
            for subcategory in response.context['categories'][0].visible_subcategories
        }
        self.assertTrue(subcategories['Carnes'].has_dish_images)
        self.assertFalse(subcategories['Pizzas'].has_dish_images)

    def test_sold_out_dish_image_does_not_reserve_space(self):
        self.sold_out.image = 'https://example.com/pollo.jpg'
        self.sold_out.save(update_fields=['image'])

        response = self.client.get(reverse('menu:index'))

        subcategory = response.context['categories'][0].visible_subcategories[0]
        self.assertFalse(subcategory.has_dish_images)
        self.assertNotContains(response, 'class="dish__media')

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

    def test_header_has_no_nav_links(self):
        response = self.client.get('/es/')
        self.assertNotContains(response, 'site-header__nav')

    def test_favicon_is_linked(self):
        response = self.client.get('/es/')
        self.assertContains(response, 'Imagenes/Icono.svg')

    def test_about_url_spanish(self):
        with translation.override('es'):
            self.assertEqual(reverse('menu:about'), '/es/sobre-nosotros/')

    def test_about_url_english(self):
        with translation.override('en'):
            self.assertEqual(reverse('menu:about'), '/en/about-us/')

    def test_about_page_renders(self):
        response = self.client.get('/es/sobre-nosotros/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vila's Restaurante nace")

    def test_about_page_english(self):
        response = self.client.get('/en/about-us/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vila's Restaurant was born")

    def test_index_has_no_about_section(self):
        response = self.client.get('/es/')
        self.assertNotContains(response, 'id="about-us"')
        self.assertNotContains(response, "Vila's Restaurante nace")

    def test_footer_links_to_about_page(self):
        response = self.client.get('/es/')
        self.assertContains(response, reverse('menu:about'))


class AdminRegistrationTests(TestCase):
    def test_models_registered_in_admin(self):
        self.assertTrue(admin.site.is_registered(Category))
        self.assertTrue(admin.site.is_registered(SubCategory))
        self.assertTrue(admin.site.is_registered(Dish))


class SupabaseStorageTests(TestCase):
    @override_settings(
        SUPABASE_STORAGE_PUBLIC_URL='https://abc.supabase.co/storage/v1/object/public/imagenes',
        AWS_STORAGE_BUCKET_NAME='imagenes',
        AWS_LOCATION='dishes/',
    )
    def test_url_returns_public_read_path(self):
        storage = SupabaseS3Storage()
        url = storage.url('dishes/foto.jpg')

        self.assertEqual(
            url,
            'https://abc.supabase.co/storage/v1/object/public/imagenes/dishes/dishes/foto.jpg',
        )
        self.assertNotIn('?', url)

    @override_settings(
        SUPABASE_STORAGE_PUBLIC_URL='https://abc.supabase.co/storage/v1/object/public/imagenes',
        AWS_STORAGE_BUCKET_NAME='imagenes',
        AWS_LOCATION='dishes/',
    )
    def test_url_encodes_special_characters(self):
        storage = SupabaseS3Storage()

        url = storage.url('dishes/foto con espacio.jpg')

        self.assertTrue(url.endswith('foto%20con%20espacio.jpg'))

    def test_url_returns_legacy_absolute_url(self):
        storage = SupabaseS3Storage()
        url = 'https://i.ibb.co/abc/foto.jpg'

        self.assertEqual(storage.url(url), url)


class CreateAdminCommandTests(TestCase):
    def _env(self, **values):
        env = {
            'DJANGO_SUPERUSER_USERNAME': '',
            'DJANGO_SUPERUSER_EMAIL': '',
            'DJANGO_SUPERUSER_PASSWORD': '',
        }
        env.update(values)
        return mock.patch.dict(os.environ, env)

    def test_skips_when_credentials_missing(self):
        with self._env():
            call_command('create_admin')
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_creates_superuser_from_env(self):
        with self._env(
            DJANGO_SUPERUSER_USERNAME='VilasProd',
            DJANGO_SUPERUSER_EMAIL='admin@vilas.test',
            DJANGO_SUPERUSER_PASSWORD='ClaveSegura123',
        ):
            call_command('create_admin')

        user = get_user_model().objects.get(username='VilasProd')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.email, 'admin@vilas.test')
        self.assertTrue(user.check_password('ClaveSegura123'))

    def test_is_idempotent_and_keeps_password(self):
        with self._env(
            DJANGO_SUPERUSER_USERNAME='VilasProd',
            DJANGO_SUPERUSER_PASSWORD='ClaveOriginal123',
        ):
            call_command('create_admin')
        with self._env(
            DJANGO_SUPERUSER_USERNAME='VilasProd',
            DJANGO_SUPERUSER_PASSWORD='ClaveNueva456',
        ):
            call_command('create_admin')

        users = get_user_model().objects.filter(username='VilasProd')
        self.assertEqual(users.count(), 1)
        self.assertTrue(users.first().check_password('ClaveOriginal123'))
