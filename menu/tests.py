import os
from decimal import Decimal
from unittest import mock

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from .models import Category, Dish, SubCategory
from .storage import ImgBBStorage


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


class ImgBBStorageTests(TestCase):
    def setUp(self):
        self.storage = ImgBBStorage()

    @override_settings(IMGBB_API_KEY='test-key')
    def test_save_returns_direct_url_on_success(self):
        content = ContentFile(b'fake-image-bytes', name='foto.jpg')
        response = mock.Mock(status_code=200)
        response.json.return_value = {
            'success': True,
            'data': {'url': 'https://i.ibb.co/abc/foto.jpg'},
        }
        with mock.patch('menu.storage.requests.post', return_value=response) as post:
            result = self.storage._save('dishes/foto.jpg', content)

        self.assertEqual(result, 'https://i.ibb.co/abc/foto.jpg')
        self.assertEqual(post.call_args.kwargs['params'], {'key': 'test-key'})
        self.assertEqual(post.call_args.kwargs['files']['image'][0], 'foto.jpg')

    @override_settings(IMGBB_API_KEY='test-key')
    def test_save_raises_when_api_reports_failure(self):
        content = ContentFile(b'fake-image-bytes', name='foto.jpg')
        response = mock.Mock(status_code=200)
        response.json.return_value = {'success': False, 'error': {'message': 'boom'}}
        with mock.patch('menu.storage.requests.post', return_value=response):
            with self.assertRaises(RuntimeError):
                self.storage._save('dishes/foto.jpg', content)

    @override_settings(IMGBB_API_KEY='test-key')
    def test_save_raises_on_non_200_status(self):
        content = ContentFile(b'fake-image-bytes', name='foto.jpg')
        response = mock.Mock(status_code=500)
        response.json.return_value = {'success': True, 'data': {'url': 'x'}}
        with mock.patch('menu.storage.requests.post', return_value=response):
            with self.assertRaises(RuntimeError):
                self.storage._save('dishes/foto.jpg', content)

    @override_settings(IMGBB_API_KEY='')
    def test_save_without_api_key_raises_improperly_configured(self):
        content = ContentFile(b'fake-image-bytes', name='foto.jpg')
        with self.assertRaises(ImproperlyConfigured):
            self.storage._save('dishes/foto.jpg', content)

    def test_url_returns_name_and_exists_is_false(self):
        url = 'https://i.ibb.co/abc/foto.jpg'
        self.assertEqual(self.storage.url(url), url)
        self.assertFalse(self.storage.exists('dishes/foto.jpg'))

    def test_open_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.storage._open('dishes/foto.jpg')


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
